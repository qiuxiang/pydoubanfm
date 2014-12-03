class Hook:
    def __init__(self):
        self.hooks = {}

    def on(self, hook, function=None):
        if type(hook) is dict:
            for hook_name, function in hook.iteritems():
                self.put(hook_name, function)
        else:
            self.put(hook, function)

    def put(self, hook_name, function):
        if hook_name in self.hooks:
            self.hooks[hook_name].append(function)
        else:
            self.hooks[hook_name] = [function]

    def dispatch(self, hook_name):
        if hook_name in self.hooks:
            for function in self.hooks[hook_name]:
                function()
