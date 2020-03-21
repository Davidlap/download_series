# Description

This scripts uses a JSON config file, with series you are currently watching, you can update it and update the date a new episode is released (if: Monday == 0, Tuesday == 1...), you can set it up to run every day at any time, is advisable to schedule it few hours after the episode was released in the original country so it has time to be also in torrent

# Requirements
  Following python3 libraries, you can install all of them with ```pip install requirements.txt```
      beautifulsoup4==4.8.2
      certifi==2019.11.28
      chardet==3.0.4
      idna==2.9
      requests==2.23.0
      soupsieve==2.0
      urllib3==1.25.8
  
  You need to have installed a torrent client
  
# Supported OS
  - Windows
  - Linux -- in progress
  
# How to use it
- Modify series_config.json and add you favorites shows with the release date, then create a schedule job in windows to run the script everyday. Follow naming standard like below
```json
{
    "series":{
        "Modern Family":{
            "release_date": 3
        },
        "Westworld":{
            "release_date": 5
        }
    }
}
```


Enjoy
