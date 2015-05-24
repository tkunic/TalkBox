#!/usr/bin/env python

import logging
import os
import subprocess

import re
import json

import pygame
import web

# import RPi.GPIO as GPIO
# import mpr121


logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

conf_dir = '/home/usman/Downloads/TalkBox-master/conf'
num_pins = 12 # FIXME: kinda stuck at 12 due to Upload.POST

class SoundSet():
    """Contains one pin to soundfile mapping."""
    def __init__(self, soundset_dir=os.path.join(conf_dir,'month')):
        self.soundset_dir = soundset_dir
        self.conf_file = os.path.join(soundset_dir, 'soundconf.json')
        self.conf = {}
        try:
            with open(self.conf_file, 'r') as fin:
                self.conf = json.load(fin)
        except:
            logging.error('Failed to read the conf file at %s' % self.conf_file)
            self.play_sentence("Talk Box failed to load configuration. Please reboot or contact gamay lab.")
            exit(1)

        self.name_file = self.conf['soundset_filename']
        self.name_sound = self.create_sound(self.name_file)

        self.pins = {}
        for i in xrange(1,num_pins + 1):
            pin_conf = self.conf[str(i)]
            filename = pin_conf['filename']
            self.pins[i] = {}
            self.pins[i]['filename'] = filename
            if filename != "":
                self.pins[i]['sound'] = self.create_sound(filename)
            else:
                self.pins[i]['sound'] = None

        self.play_name()

    def create_sound(self, sound_file):
        sound = pygame.mixer.Sound(sound_file)
        sound.set_volume(1.0)
        return sound

    def get_pin_file(self, pin_num):
        return self.pins[pin_num]['filename']

    def play_pin(self, pin_num):
        sound = self.pins[pin_num]['sound']
        if sound:
            sound.play()
        else:
            logging.warning("Sound not set for pin %d" % pin_num)

    def get_name_file(self):
        return self.name_file

    def play_name(self):
        self.name_sound.play()

    def get_dir(self):
        return self.soundset_dir

    def play_sentence(self, sentence):
        sentence_file = '/tmp/tbsentence.wav'
        subprocess.Popen(['espeak', '"', sentence, '"', '-w', sentence_file], stdout=subprocess.PIPE)
        self.create_sound(sentence_file).play()


class Vocabulary:
    def GET(self):
        global sound_set
        web.header("Content-Type", "text/html; charset=utf-8")

        # TODO: Migrate to web.py templates
        result_list = []
        result_list.append("""<html>
<head>
    <meta charset="utf-8">
    <link href="/static/style.css" type="text/css" rel="stylesheet">
    <link rel="stylesheet" href="/static/css/bootstrap.min.css">
    <link rel="stylesheet" type="text/css" href="/static/css/style.css" />    

    <script type="text/javascript">
        
        function addOption(theSel, theText, theValue)
        {
          var newOpt = new Option(theText, theValue);
          var selLength = theSel.length;          
          theSel.options[selLength] = newOpt;
        }

        function deleteOption(theSel, theIndex)
        { 
          var selLength = theSel.length;
          if(selLength>0)
          {
            theSel.options[theIndex] = null;
          }
        }

        function moveOptions(theSelFrom, theSelTo)
        {
          var selLength = theSelFrom.length;
          var selectedText = new Array();
          var selectedValues = new Array();
          var selectedCount = 0;
          
          var i;
          
          // Find the selected Options in reverse order
          // and delete them from the 'from' Select.
          for(i=selLength-1; i>=0; i--)
          {
            if(theSelFrom.options[i].selected)
            {
              selectedText[selectedCount] = theSelFrom.options[i].text;
              selectedValues[selectedCount] = theSelFrom.options[i].value;
              
                if(!(theSelFrom.name == "sel2"))
                {
                    deleteOption(theSelFrom, i);                    
                }
                selectedCount++;
            }
          }
          
          // Add the selected text/values in reverse order.
          // This will add the Options to the 'to' Select
          // in the same order as they were in the 'from' Select.
          for(i=selectedCount-1; i>=0; i--)
          {
            if(!(theSelTo.name == "sel2") && (theSelTo.length < 12))
            {
                addOption(theSelTo, selectedText[i], selectedValues[i]);
            }
          }          
        }
    </script>
</head>
<body>

<header>
        <center>
            <img src="/static/img/rsz_talkbox_logo.png" alt="TalkBox"/>
            <font size="20px">
                The TalkBox Project
            </font>
        </center>
        <div class="nav">
          <ul>
            <li class="home"><a id="h" href="/" >Home</a></li>
            <li class="sounds"><a id="s" href="/sound" >Sound(s)</a></li>
            <li class="vocabularies"><a id="v" class="active" href="#" >Vocabulary(s)</a></li>                    
          </ul>
        </div>      
</header>

    <div align="center" id="ss">
    <center> <h1>Vocabulary Files</h1> </center>

        <div style="width:50%; float:left" align="center">
            <form method="POST" action="/vocab_search">
                
                <table>

                    <tr>
                        <td>
                            <div class="form-group">
                              <label>Enter RFID : </label>
                            </div>
                        </td>
                        <td>
                            <div class="form-group">
                                <input type="text" class="form-control" name="search_rfid" />
                            </div>                            
                        </td>
                    </tr>
                    <tr>
                        <td></td>
                        <td>
                            <input type="submit" class="btn btn-default" name="rfid_search" value="Search" />
                        </td>
                    </tr>

                </table>        

            </form>
        </div>

        <div style="width:50%; float:right" align="left">
                
                <table>
                <tr>
                    <th>                    
                    <form method="POST" action="/vocab_save">
                        <table>
                            <tr>
                                <td>You can choose up to 12 sounds</td>
                            </tr>
                            <tr>
                                <td>
                                    <div class="form-group">
                                      <label>Enter RFID : </label>
                                    </div>                                
                                    <div class="form-group">
                                        <input type="text" class="form-control" name="rfid_no" />
                                    </div>                            
                                </td>                                
                            </tr>
                            <tr>
                                <td>
                                    <div class="form-group">                            
                                      <label>My Vocabulary</label>                                      
                                    </div>
                                </td>                            
                            </tr>
                            <tr>
                                <td>
                                    <select name="sel1" size="10" >\n""")

        for mysoundfile in os.listdir(os.path.basename("/sounds")):
            if os.path.isfile(os.path.join(os.path.basename("/sounds"),mysoundfile)):
                result_list.append("""<option value="%s">%s</option>""" % (mysoundfile, mysoundfile))
            else:
                print mysoundfile
        result_list.append("""        
                                    </select>

                                </td>                            
                            </tr>                            
                            <tr>
                                <td>
                                    <input type="submit" class="btn btn-default" name="add_rfid" value="Save" />
                                </td>
                            </tr>                            
                            
                        </table>                    
                    </th>

                    <th align="center" valign="middle" style="padding:20px;">
                        <input type="button" value="--&gt;" class="btn btn-default" onclick="moveOptions(this.form.sel1, this.form.sel2);" />
                        <br />
                        <input type="button" value="&lt;--" class="btn btn-default" onclick="moveOptions(this.form.sel2, this.form.sel1);" />
                    </th>

                    <th>                    
                        <table>
                            <tr>
                                <div class="form-group">
                                      <label></label>
                                    </div>                                
                                    <div class="form-group">
                                        
                                    </div>                            
                            </tr>
                            <tr>
                                <div class="form-group">
                                      <label></label>
                                    </div>                                
                                    <div class="form-group">
                                        
                                    </div>                            
                            </tr>
                            <tr>
                                <div class="form-group">
                                      <label></label>
                                    </div>                                
                                    <div class="form-group">
                                        
                                    </div>                            
                            </tr>
                            <tr>
                                <td>
                                    <div class="form-group">
                                      <label>List of All Sounds</label>
                                    </div>
                                </td>                            
                            </tr>
                            <tr>
                                <div class="form-group">
                                      <label></label>
                                    </div>                                
                                    <div class="form-group">
                                        
                                    </div>                            
                            </tr>
                            <tr>
                                <td>
                                    <select name="sel2" size="10" >\n""")

        for mysoundfile in os.listdir(os.path.basename("/sounds")):
            if os.path.isfile(os.path.join(os.path.basename("/sounds"),mysoundfile)):
                result_list.append("""<option value="%s">%s</option>""" % (mysoundfile, mysoundfile))
            else:
                print mysoundfile
        result_list.append("""        
                                    </select>

                                </td>                            
                            </tr>
                            <tr><td></td></tr>
                            <tr><td></td></tr>
                            <tr><td></td></tr>
                        </table>

                    </form>
                    </th>
                </tr>
                </table>
            </div>
    </div>

</body>
</html>""")
        return ''.join(result_list)

    def POST(self):        
        global sound_set
        # TODO: this is silly, but didn't find a better way quickly enough.
        x = web.input(sounds_list={})
        slist = x.sounds_list
        selected_file = slist

        # Write the uploaded file to filedir
        file_destination_path = ''
        if selected_file is not None and selected_file != '':
            # TODO: what if someone uploads blap.wav to pin 3 even though it
            # is already on pin 2 and the blap.wav files are different despite
            # the same name? Rename to blap(2).wav.
            file_destination_path = os.path.join(os.path.basename("/sounds"), selected_file)
            os.remove(file_destination_path)
        
        # FIXME: Ensure no sounds are played while this is being changed.
        sound_set = SoundSet()

        # TODO: Indicate to user that update has been successful.
        raise web.seeother('/vocab')

class RSound:
    def GET(self):
        global sound_set
        web.header("Content-Type", "text/html; charset=utf-8")

        # TODO: Migrate to web.py templates
        result_list = []
        result_list.append("""<html>
<head>
    <meta charset="utf-8">
    <link href="/static/style.css" type="text/css" rel="stylesheet">
    <link rel="stylesheet" href="/static/css/bootstrap.min.css">
    <link rel="stylesheet" type="text/css" href="/static/css/style.css" />
    <script src="/static/js/audiodisplay.js"></script>
    <script src="/static/js/recorderjs/recorder.js"></script>
    <script src="/static/js/main.js"></script>

    <style>    
    
        canvas {    
            background: #202020;        
            box-shadow: 0px 0px 10px blue;
        }
        
        #record.recording { 
            background: red;
            background: -webkit-radial-gradient(center, ellipse cover, #ff0000 0%,lightgrey 75%,lightgrey 100%,#7db9e8 100%); 
            background: -moz-radial-gradient(center, ellipse cover, #ff0000 0%,lightgrey 75%,lightgrey 100%,#7db9e8 100%); 
            background: radial-gradient(center, ellipse cover, #ff0000 0%,lightgrey 75%,lightgrey 100%,#7db9e8 100%); 
        }
        #save, #save img { height: 10vh; }
        
        #save[download] { opacity: 1;}   

    </style>
</head>
<body>

<header>
        <center>
            <img src="/static/img/rsz_talkbox_logo.png" alt="TalkBox"/>
            <font size="20px">
                The TalkBox Project
            </font>
        </center>
        <div class="nav">
          <ul>
            <li class="home"><a id="h" href="/" >Home</a></li>
            <li class="sounds"><a id="s" class="active" href="#" >Sound(s)</a></li>
            <li class="vocabularies"><a id="v" href="/vocab" >Vocabulary(s)</a></li>                    
          </ul>
        </div>      
</header>

    <div align="center" id="ss">

        <div id="sound_files">
            <center> <h1>Sound Files</h1> </center>
            
            <div style="width:50%; float:left" align="center">
                
                <form method="POST" enctype="multipart/form-data" action="/">
                
                <table>

                    <tr>
                        <td>
                            <div class="form-group">
                              <label>Sound Name</label>
                            </div>
                        </td>
                        <td>
                            <div class="form-group">
                              &nbsp; &nbsp; &nbsp; <input type="text" class="form-control" name="sound_name" />
                            </div>
                            <input type="file" name="sound_upload" accept="audio/*" />
                        </td>
                    </tr>            
                    <tr>
                        <td><img id="record" href="#" src="/static/img/rsz_mic128.png" height="50" onclick="toggleRecording(this);"></td>
                        <td>                    
                            <canvas id="analyser" height="20px"></canvas>
                        </td>
                    </tr>
                    <tr>
                        <td></td>
                        <td>
                        <a id="save" href="#" ><canvas id="wavedisplay" style="display:none;" height="20px"></canvas> </a>            
                        </td>
                    </tr>
                    <tr>
                        <td></td>
                        <td><input type="submit" class="btn btn-default" value="Save" class="savebutton" /></td>
                    </tr>

                </table>        

                </form>
            
            </div>

        <div style="width:50%; float:right" align="center">

                <form method="POST" action="/sound">
                    <table>
                        <tr>
                            <td>
                                <div class="form-group">
                                  <label>List of All Sounds</label>
                                </div>
                            </td>                            
                        </tr>
                        <tr>
                            <td>
                                <select name="sounds_list" size="10" >\n""")

        for mysoundfile in os.listdir(os.path.basename("/sounds")):
            if os.path.isfile(os.path.join(os.path.basename("/sounds"),mysoundfile)):
                result_list.append("""<option value="%s">%s</option>""" % (mysoundfile, mysoundfile))
            else:
                print mysoundfile
        result_list.append("""        
                                </select>

                            </td>

                            <td>
                                &nbsp; &nbsp; <input type="submit" class="btn btn-default" value="Delete" />
                            </td>

                        </tr>
                    </table>

                </form>

            </div>

        </div>

    </div>

</body>
</html>""")
        return ''.join(result_list)

    def POST(self):        
        global sound_set
        # TODO: this is silly, but didn't find a better way quickly enough.
        x = web.input(sounds_list={})
        slist = x.sounds_list
        selected_file = slist

        # Write the uploaded file to filedir
        file_destination_path = ''
        if selected_file is not None and selected_file != '':
            # TODO: what if someone uploads blap.wav to pin 3 even though it
            # is already on pin 2 and the blap.wav files are different despite
            # the same name? Rename to blap(2).wav.
            file_destination_path = os.path.join(os.path.basename("/sounds"), selected_file)
            os.remove(file_destination_path)
        
        # FIXME: Ensure no sounds are played while this is being changed.
        sound_set = SoundSet()

        # TODO: Indicate to user that update has been successful.
        raise web.seeother('/sound')

class Upload:
    def GET(self):
        global sound_set
        web.header("Content-Type", "text/html; charset=utf-8")

        # TODO: Migrate to web.py templates
        result_list = []
        result_list.append("""<html>
<head>
    <meta charset="utf-8">
    <link href="/static/style.css" type="text/css" rel="stylesheet">
    <link rel="stylesheet" href="/static/css/bootstrap.min.css">
    <link rel="stylesheet" type="text/css" href="/static/css/style.css" />    

</head>
<body>

<header>
        <center>
            <img src="/static/img/rsz_talkbox_logo.png" alt="TalkBox"/>
            <font size="20px">
                The TalkBox Project
            </font>
        </center>
        <div class="nav">
          <ul>
            <li class="home"><a id="h" class="active" href="#" >Home</a></li>
            <li class="sounds"><a id="s" href="/sound" >Sound(s)</a></li>
            <li class="vocabularies"><a id="v" href="/vocab" >Vocabulary(s)</a></li>                    
          </ul>
        </div>      
</header>

    
    <div align="center" id="hh">
        <h3> HOT SWAPPABLE MULTI-LINGUAL VOCABULARY SETS FOR TALKBOX </h3>
        <br />
        
        <p style="width:60%; text-align: justify; text-justify: inter-word;">
            The <a href="http://link.springer.com/chapter/10.1007%2F978-3-319-08599-9_44">TalkBox</a> is a low cost Do-It-Yourself (DIY) form of Speech Generation Device (SGD). 
            SGDs assist people who are functionally non-verbal with the ability to communicate through a means of vocabulary selection and 
            speech synthesis.  In practice, obtaining a commercial SGD depends on successfully navigating several issues.  
            These issues are numerous but are typically associated with finances and adaptability, or customizability.  
            In general, SGD suffer from the same issues that other assistive technologies face - meaningful dissemination.  
            The principles that normally keep our economies in check, do not typically apply to assistive technologies.  
            That is, the achievement of economy of scale as a result of supply and demand is nearly impossible given the relative lack of demand. 
            In Ontario, it could be years between when the needs of a particular student are identified and when the device is received. 
            This means that the devices are not only hard to get but also less customizable and usable, since commercial products tend to 
            follow a one-size-fits-all approach in order to achieve mass production.  That is, the vocabularies and physical makeup of the 
            device is typically static and, as such, in danger of becoming physically or contextually irrelevant, and ultimately unusable. 
            The TalkBox aims to bridge these gaps present in the current delivery of commercial SGDs. 
        </p>

        <footer>
            <img src="/static/img/gamay_logo.png" alt="TalkBox" width="25%" height="15%" style="float:left; padding-top:15px;"/>
            <img src="/static/img/yorku_logo.png" alt="TalkBox" width="25%" height="15%" style="float:right;padding-top:15px;"/>
        </footer>
    </div>

</body>
</html>""")
        return ''.join(result_list)

    def POST(self):
        global sound_set
        # TODO: this is silly, but didn't find a better way quickly enough.
        x = web.input(sound_upload={})
        store_sound = x.sound_upload
        
        # TODO: use os.path for most of this.
        input_filepath = store_sound.filename.replace('\\', '/')
        input_filename = input_filepath.split('/')[-1]

        # Write the uploaded file to filedir
        file_destination_path = ''
        if input_filename is not None and input_filename != '':
            # TODO: what if someone uploads blap.wav to pin 3 even though it
            # is already on pin 2 and the blap.wav files are different despite
            # the same name? Rename to blap(2).wav.
            file_destination_path = os.path.join(os.path.basename("/sounds"), input_filename)
            with open(file_destination_path, 'w') as fout:
                fout.write(store_sound.file.read())
                fout.close()
        
        # FIXME: Ensure no sounds are played while this is being changed.
        sound_set = SoundSet()

        # TODO: Indicate to user that update has been successful.
        raise web.seeother('/sound')

    def update_pin_config(self, pin_num, file_name):
        # Update the configuration file with the new filenames.
        try:
            conf_file = os.path.join(sound_set.get_dir(), 'conf.json')
            conf = None;

            # Get current contents of config file
            with open(conf_file, 'r') as fin:
                conf = json.load(fin)

            # Write updated config back
            with open(conf_file, 'w') as fout:
                conf[str(pin_num)]['filename'] = file_name
                json.dump(conf, fout, indent=4)

        except Exception as e:
            logging.error("ERROR: failed to write configuration due to: '%s'" % e.message)
            # TODO: actually display this in the browser as feedback to the user
            sound_set.play_sentence("ERROR: failed to write configuration")

class TalkBoxWeb(web.application):
    def run(self, port=8080, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))


def handle_touch(channel):
    touchData = mpr121.readWordData(0x5a)
    if not pygame.mixer.get_busy(): # if no sound is playing
        for i in xrange(num_pins):
            if (touchData & (1<<i)):
                sound_set.play_pin(i + 1)


if __name__ == "__main__":
    # # Init GPIO Interrupt Pin
    # GPIO.setmode(GPIO.BOARD)
    # GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # # Init mpr121 touch sensor
    # mpr121.TOU_THRESH = 0x30
    # mpr121.REL_THRESH = 0x33
    # mpr121.setup(0x5a)

    # # Init Pygame
    pygame.mixer.pre_init(44100, -16, 12, 512)
    pygame.init()

    # # FIXME: shouldn't be global, but short on time
    sound_set = SoundSet()
    # # Add callback to pin 7 (interrupt)
    # GPIO.add_event_detect(7, GPIO.FALLING, callback=handle_touch)

    # Init Web (which in turn inits buttons)
    # TODO: add further URLs, for example to test I2C and other statuses.
    urls = (
        '/', 'Upload',
        '/sound', 'RSound',
        '/vocab', 'Vocabulary'
        )
    app = TalkBoxWeb(urls, globals())
    app.run(port=80)

