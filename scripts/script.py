import requests, base64, os, argparse


## HOWTO:
## Make sure A1111 has API access enabled (in A1111/webui/webui-user.bat, line "set COMMANDLINE_ARGS=" add "--api")
## Set the desired input directory a few lines below (in the file you are currently reading)
## Check that the url (and port) is correct
## Run! (wait) Succes!


## DIRECTORIES
dir_in = r"../input/"                    # Input directory with images to process
dir_out = r"../output/"                  # Output directory (default: new directory inside input dir)
url_default = "http://127.0.0.1:7860/"   # URL used to connect with A1111 ControlNet (default: http://127.0.0.1:7860/)
controlnet_default = "dw_openpose_full"  # Which preprocessor to use.
res_default = 512                        # What resolution to run the ControlNet pre-processor at. (default: 512)


if __name__ == "__main__":
  ## Command-line arguments
  parser = argparse.ArgumentParser(description="Process a batch of images through a ControlNet sequentially.")
  parser.add_argument("-u", "--url",        help=f"The URL to use to interact with A1111's SD web UI.  Default: {url_default}",       type=str, default=url_default)
  parser.add_argument("-c", "--controlnet", help=f"Which ControlNet to run the input images through.  Default: {controlnet_default}", type=str, default=controlnet_default)
  parser.add_argument("-r", "--resolution", help=f"Resolution to run the ControlNet at.  Default: {res_default}",                     type=int, default=res_default)
  parser.add_argument("-l", "--list",       help="List out all available ControlNets.",                                               action="store_true")
  parser.add_argument("-a", "--arga",       help=f"First argument passed (like Low Threshold).  Defaults can be found by using -c [controlnet] -l",       type=float, default=float('nan'))
  parser.add_argument("-b", "--argb",       help=f"Second argument passed (like High Threshold).  Defaults can be found by using -c [controlnet] -l",     type=float, default=float('nan'))

  ## Command-line argument checking and correction
  def controlnet_arg_check(_controlnet, _res, _args):
    response = requests.get(f"{url}controlnet/module_list?alias_names=true", headers={"accept":"application/json"})
    if (response.status_code != 200):
      raise ConnectionError(f"Could not reach controlnet via API. Check if the URL ({url}) is correct, api-mode is enabled, and A1111 is running. If all those are working, it could be that the API is in a different format than this script expects (i.e. newer), if that's the case, please submit an issue to the repository of this script including the version of A1111 and Controlnet you are using (and possibly other extensions), thank you.")
    if (response.json()["module_list"].count(_controlnet) != 1):
      raise NameError(f"controlnet ({_controlnet}) not found (or multiple with the same name)")
    details = response.json()["module_detail"][_controlnet]
    #print(f"@@ details: {details}")
    #print(f"@@ {len(details['sliders'])}")
    #while (len(details["sliders"]) < 3):
    #  details["sliders"].append({'name': 'controlnet_threshold_placeholder', 'min': 0, 'max': 2, 'value': 1})
    argN = 0
    _args = list(_args)
    _argnames = list(("controlnet_threshold_PLACEHOLDER", "controlnet_threshold_PLACEHOLDER"))
    for item in details["sliders"]:
      if (item != None):
        if (item["name"] == "Preprocessor Resolution"):
          if (item["min"] > _res):
            print(f"WARNING! specified resolution ({_res}) is less than minimum ({item['min']}), rounding up to minimum!")
            _res = item["min"]
          elif (item["max"] < _res):
            print(f"WARNING! specified resolution ({_res}) is more than maximum ({item['max']}), rounding down to maximum!")
            _res = item["max"]
        else:
          arg = _args[argN]
          if (arg == arg):  # if arg != nan
            try:
              tmp = arg % item["step"]
              if (tmp != 0):
                arg = arg // item["step"] * item["step"]
                print(f"WARNING! Value of the {argN+1}st argument ({item['name']}) must be divisible (stepped) by {item['step']}! Rounding it down to ({arg})!")
            except:  # value doesn't have to be stepped
              pass
            if (item["min"] > arg):
              print(f"WARNING! argument {argN+1} ({arg}) ({item['name']}) is less than minimum ({item['min']}), rounding up to minimum!")
              arg = item["min"]
            elif (item["max"] < arg):
              print(f"WARNING! argument {argN+1} ({arg}) ({item['name']}) is more than maximum ({item['max']}), rounding down to maximum!")
              arg = item["max"]
          else:
            print(f"No value provided for argument {argN+1} ({item['name']}), using default ({item['value']})")
            arg = item['value']
          _args[argN] = arg
          _argnames[argN] = item["name"]
          argN += 1
    return (_controlnet, _res, _args, _argnames)

  ## Command-line argument handling
  args = parser.parse_args()
  url = args.url
  if not (url.startswith("http://") or url.startswith("https://")):
    url = "http://" + url
  if not (url.endswith("/")):
    url = url + "/"
  controlnet = args.controlnet
  if (not args.list):
    new_settings = controlnet_arg_check(controlnet, args.resolution, (args.arga, args.argb))
    resolution = new_settings[1]
  print(f"URL: {url}")
  print(f"ControlNet: {controlnet}")

  ## ControlNet selector
  if (args.list == True):
    print("Listing all available controlnets.")
    nets = []
    response = requests.get(f"{url}controlnet/module_list?alias_names=true", headers={"accept":"application/json"})
    nets = response.json()["module_list"]
    print("\nAvailable ControlNets:")
    for net in nets:
      print(net, end=', ')
    tmp = response.json()["module_detail"][controlnet]
    #print(type(tmp), tmp)
    controlnet_args = ""
    for item in tmp["sliders"]:
      if (item != None):
        if (item["name"] != "Preprocessor Resolution"):
          controlnet_args += f"\n  {item['name']}: {item['min']}~{item['max']} default:{item['value']}"
          try:
            controlnet_args += f" stepsize:{item['step']}"
          except:
            pass
    print(f"\n\nParameters available for selected controlnet ({controlnet}): {controlnet_args}")
    print(f"For more details on which parameters are usable, see {url_default}docs#/default/module_list_controlnet_module_list_get")


  else:
    ## Directory and file stuff
    dir_start = os.getcwd() + '/'
    dir_in = dir_start + dir_in
    dir_out = dir_start + dir_out
    if not (dir_in.endswith('/') or dir_in.endswith("\\")):
      dir_in += "/"
    if not (dir_out.endswith('/') or dir_out.endswith("\\")):
      dir_out += "/"
    if not (os.path.exists(dir_out)):
      print(f"Output directory doesn't exist, creating it! {dir_out}")
      os.makedirs(dir_out)
    files_tmp = os.listdir(dir_in)
    files = []
    for filename in files_tmp:
      if (filename.endswith('png') or filename.endswith('jpg') or filename.endswith('jpeg') or filename.endswith('gif') or filename.endswith('bmp')):
        print(f"Found image! {filename}")
        files.append(filename)

    ## Loop through images
    for filename in files:
      print(f"..Processing {filename}   @ (res:{resolution}", sep='', end='')
      if (new_settings[2][0] == new_settings[2][0]):
        print(f" a:{new_settings[2][0]}", sep='', end='')
      if (new_settings[2][1] == new_settings[2][1]):
        print(f" b:{new_settings[2][1]}", sep='', end='')
      print(')')
      ## Encode image in base64
      with open(dir_in + filename, 'rb') as file:
        image_data = base64.encodebytes(file.read())
        data = "{" \
          '"controlnet_module": "' + controlnet + '",' \
          '"controlnet_input_images": ["data:image/png;base64,' + str(image_data)[2:-3] + '"],' \
          '"controlnet_processor_res": ' + str(resolution)
        if (new_settings[2][0] == new_settings[2][0]):
          data += ',' \
          '"' + str(new_settings[3][0]) + '": ' + str(new_settings[2][0])
          if (new_settings[2][1] == new_settings[2][1]):
            data += ',' \
            '"' + str(new_settings[3][1]) + '": ' + str(new_settings[2][1]) + '}'
          else:
            data += '}'
        else:
          data += '}'
        #debug print(data)

      ## Send request to ControlNet
      headers = {"accept":       "application/json",
                 "Content-Type": "application/json"}
      response = requests.post(url + "controlnet/detect", data=data, headers=headers)
      response_json = response.json()
      if (response.status_code == 200):  # Succes
        if (response_json["info"] == "Success"):
          ## Save image
          if (len(response_json["images"][0]) != 0):
            image_data = base64.decodebytes(bytes(response_json["images"][0], 'ascii'))
            with open(dir_out + filename, 'wb') as file:
              file.write(image_data)
          else:
            print(f"{filename} returned an empty image.")
          ## save json
          if ("poses" in response_json.keys()):
            with open(dir_out + filename + ".json", 'w') as file:
              file.write(str(response_json["poses"][0]).replace(' ',''))
        else:
          print(f"{filename}'s processing wasn't succesful.\t{response_json['info']}")
      else:  # Failure
        response.raise_for_status()
    print(f"Done!\n  Output in directory: {dir_out}")
