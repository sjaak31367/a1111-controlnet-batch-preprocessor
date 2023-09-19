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

  ## Command-line argument handling
  args = parser.parse_args()
  url = args.url
  if not (url.startswith("http://") or url.startswith("https://")):
    url = "http://" + url
  if not (url.endswith("/")):
    url = url + "/"
  controlnet = args.controlnet
  if ((args.resolution < 64) or args.resolution > 2048):
    raise ValueError(f"Resolution outside bounds! (min: 64, max: 2048, resolution: {args.resolution})")
  resolution = args.resolution
  print(f"URL: {url}")
  print(f"ControlNet: {controlnet}")

  ## ControlNet selector
  if (args.list == True):
    print("Listing all available controlnets.")
    nets = []
    response = requests.get(url + "controlnet/module_list?alias_names=true", headers={"accept":"application/json"})
    nets = response.json()["module_list"]
    print("\nAvailable ControlNets:")
    for net in nets:
      print(net, end=', ')
    print(f"\n\nFor details on which parameters are usable, see {url_default}docs#/default/module_list_controlnet_module_list_get")

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
      print(f"..Processing {filename}")
      ## Encode image in base64
      with open(dir_in + filename, 'rb') as file:
        image_data = base64.encodebytes(file.read())
        data = "{" \
          '"controlnet_module": "' + controlnet + '",' \
          '"controlnet_input_images": ["data:image/png;base64,' + str(image_data)[2:-3] + '"],' \
          '"controlnet_processor_res": ' + str(resolution) + ',' \
          '"controlnet_threshold_a": 64,' \
          '"controlnet_threshold_b": 64}'

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
