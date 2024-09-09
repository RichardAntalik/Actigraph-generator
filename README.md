# Actigraph-generator
This generates actigram image from sleep log

The sleep log file should look like this:

```
wakeup: 01.12.2023 06:00:00
bedtime: 01.12.2023 22:00:00
wakeup: 02.12.2023 06:00:00 # Some comment.
bedtime: 02.12.2023 22:00:12
wakeup: 03.12.2023 06:00:12
bedtime: 03.12.2023 21:53:57
wakeup: 04.12.2023 06:00:14
bedtime: 04.12.2023 22:00:35
```

EU time format is used, but this is easily changed.

The output looks like this:
![The graph](/act1.PNG)
Note, that this is not how actigraph for normal person should look like...
