This approach uses libraries in Linux, so it needs to be run in a Linux environment (or a Linux VM).

Start the VM:
```
vagrant up
vagrant provision #if necessary
vagrant ssh
```
Inside the ssh session, run the following commands:
```
cd /vagrant
python midi_to_mp3.py #output file will be in the output folder
```