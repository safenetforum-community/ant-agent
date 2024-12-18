## 01-download-files.csv

A control file, that is used by the agent, in providing files to download.

*to-do : it is anticipated that this file, along with revisions will be stored on the network with a register linking it.

Files can be added by, uploading them to the Autonomi network and making a note of the **filename, the autonomi network address, and a MD5 checksum** of the file.  This can then be appended to this file, and agents will automatically start to processs
the additions as part of any task definitions.

## format

Always check the csv file for the latest format changes;

`filesize, filename, autonomi network address, md5hash`

i.e

**with md5**

large,my-file.iso,0430s93943599s7d9ds97g79gd9g7d6gd5g5d66g7d7g77dg8d8g8d8g8d8g8d,79054025255fb1a16e4bc499aef54eb4

**without md5**

large,my-file.iso,0430s93943599s7d9ds97g79gd9g7d6gd5g5d66g7d7g77dg8d8g8d8g8d8g8d,0

### file sizes

To enable the tasks to better target files, the size of files is broken down into various tags, please ensure you tag the file appropriately.
```
    tiny = files with a size below 128k
    small = files with a size of 129k > 4Mb
    medium = files with a size of 4Mb > 32MB
    large = files with a size of 32MB > 60MB
    huge = files with a size of 128MB > 1G
    giga = files with a size of 1G > 20G
    tera = files with a size of 20G > 100G
    chunka = file with a size of exactly 4Mb
    chunkb = file with a size of exactly 64MB
```
### md5 checksum hash

Before uploading the file to the network, it would be useful if you made a note of the MD5 hash of the file - this can be recorded in the csv file, which the agent will then use to ensure the file downloaded matches what was uploaded.

on linux;

`md5sum filename`
