# makr
tools for recursive make in projects organized by [principled data processing](https://hrdag.org/2016/06/14/the-task-is-a-quantum-of-workflow/).

Install from this directory with `python setup.py install`.

Run the tests from this directory with `python setup.py test`.

Then use the tool by cd'ing into your favorite principled data processing task, and saying `$ makr`. That will run make (whether or not the Makefile is in the task or src/ directory). If you give the command as `makr -r`, it will extract the dependencies from the Makefile, sort them topologically, and make the tasks in order to update the current task.

<!-- done -->
