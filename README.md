# monitor-lizard
A easy system to monitor all activity on a linux device

Run ./setup.sh 

Run sudo python3 monitor.py

## Args
- keylogger | Activates the key logger | Ex. sudo python3 monitor.py keylogger
- chrome-manual | Allows you to ru chrome from your terminal. See options section below | Ex. sudo python3 monitor.py chrome-manual

## Options:
To run chrome from a separate terminal tab (this way when you end the program chrome wont close) run monitor.py chrome-manual and start chrome from a separete terminal tab

To run as a background process run nohup python3 -u ~/{insert path to program}/monitor.py chrome-manual keylogger > output.log &

Note: You must launch chrome from your terminal for the monitor to pick up your traffic.

## How to Contribute

- Fork the Repository

- Clone the Forked repository

##### ` git clone https://github.com/<USER_NAME>/<REPO_NAME>`

- Add Scripts and necessary changes

##### ` git add .`

- Commit the changes

##### `git commit -m "MESSAGE"`

- Push to your branch

##### `git push`

- Raise a Pull Request to the parent Repository
