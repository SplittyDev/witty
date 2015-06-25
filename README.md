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
```ini
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
  # called by witty when a message arrives
  def privmsg(self, user, channel, msg):
    # get the bot instance
    witty = PluginManagerSingleton.get().app
    # echo everything said in the channel
    witty.say(channel, '%s said: %s' % (user, msg))

```

### Advanced plugin example
`advanced.yapsy-plugin`:
```ini
[Core]
Name = Advanced plugin
module = advanced

[Documentation]
Author = SplittyDev
Version = 1.0
Description = A more advanced plugin
```

`advanced.py`:
```python
from yapsy.IPlugin import IPlugin
from yapsy.PluginManager import PluginManagerSingleton

class AdvancedPlugin(IPlugin):
  # automatically set by witty
  # doesn't need to be declared here
  plugin_name = None
  config = None
  
  # optional, used by witty
  usage = '_register'
  default_config = {
    'users': []
  }
  
  # called by witty on startup and plugin reload
  def init(self):
    self.manager = PluginManagerSingleton.get()
    # fill the user list with values from the config
    self.users = self.config['users']
  
  # called by witty when a message arrives
  def privmsg(self, user, channel, msg):
    if msg == '_register':
      if not user in self.users:
        self.users.append(user)
        # save the user list to the config
        self.config['users'] = self.users
        self.manager.wittyconf.update_plugin_conf(self.plugin_name, self.config)
        self.manager.app.say(channel, '%s registered!' % user)
```
