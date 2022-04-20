#!/usr/bin/env python
import ramona


class FooConsoleApp(ramona.console_app):
    pass

if __name__ == '__main__':
    app = FooConsoleApp(configuration='./fake')
    app.run()
