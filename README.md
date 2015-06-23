# witty
A small irc bot with plugin support.

## Dependencies
- Twisted
- yapsy
- Python 2.7

## Plugins
### How to write a plugin
You'll need to create two files in the `src/plugins` directory:
- plugin_name.py
- plugin_name.yapsy-plugin

You can arrange your plugins in subfolders.  
Witty doesn't care where they are as long as it
can find them anywhere in the `plugins` folder.

`plugin_name.yapsy-plugin` should look like this:
```
[Core]
Name = Name of your plugin
Module = Name of the python file containing your plugin code without `.py`

[Documentation]
Author = Your name/nick
Version = 1.0
Description = This is my awesome plugin
```

Now you can start writing the plugin code!  
`plugin_name.py`:
```python
from yapsy.IPlugin import IPlugin
from yapsy.PluginManager import PluginManagerSingleton

class EchoPlugin(IPlugin):
  def privmsg(self, user, channel, msg):
    witty = PluginManagerSingleton.get().app
    # echo everything said in the channel
    witty.say(channel, '%s said: %s' % (user, msg))

```
