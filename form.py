import web
import json
import os.path

pins = []
conf = {}
for i in range(1, 13):
    pin = 'pinfile%d' % i
    pins.append(pin)
    conf[pin] = ''

filedir = 'conf/'
conf_file_path = filedir + 'conf.json'

try:
    with open(conf_file_path, 'r') as fin:
        conf = json.load(fin)
except:
    pass # In case we failed to read the conf file, we simply continue with an empty one.

urls = ('/', 'Upload')

class Upload:
    def GET(self):
        web.header("Content-Type", "text/html; charset=utf-8")
        # Migrate to web.py templates
        result = """<html>
<head>
    <link href="/static/style.css" type="text/css" rel="stylesheet">
</head>
<body>
<img src="static/talkbox_logo.png" id="talkboxlogo">
<form method="POST" enctype="multipart/form-data" action="">\n"""
        for i, pin in enumerate(pins):
            result += """<div class="pinrow">
    <div class="pinnumber float-left">%d</div>
    <div class="filename float-left">%s</div>
    <div class="uploadbutton float-left">+<input type="file" name="%s" accept="audio/*" /></div>
</div>""" % (i + 1, os.path.basename(conf[pin]) if conf[pin] != '' else "No File", pin)
        result += """<input type="submit" value="Save" class="savebutton"/>
</form>
</body>
</html>"""
        return result

    def POST(self):
        # TODO: this is silly, but didn't find a better way quickly enough.
        x = web.input(pinfile1={},pinfile2={},pinfile3={},pinfile4={},pinfile5={},pinfile6={},pinfile7={},pinfile8={},pinfile9={},pinfile10={},pinfile11={},pinfile12={})
        for filefield in x.keys():
            filepath = x[filefield].filename.replace('\\', '/')
            filename = filepath.split('/')[-1]
            
            # Write the uploaded file to filedir
            if filename is not None and filename != '':
                # TODO: what if someone uploads blap.wav to pin 3 even though it is already on pin 2 and the blap.wav files are different despite the same name? Rename to blap(2).wav.
                file_destination_path = filedir + filename
                with open(file_destination_path, 'w') as fout:
                    conf[filefield] = file_destination_path
                    fout.write(x.get(filefield).file.read())
                    fout.close()

        # Update the configuration file with the new filenames.
        try:
            with open(conf_file_path, 'w') as fout:
                json.dump(conf, fout, indent=4)
                # TODO: indicate success to user
        except Exception as e:
            # TODO: actually display this in the browser as feedback to the user
            print "ERROR: failed to write configuration!", e.message

        raise web.seeother('/')

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
