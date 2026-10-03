# Connecting to DCE
## Data Centre d'Enseignement

Official documentation: <https://dce.pages.centralesupelec.fr/>

### Connecting with SSH

```bash
ssh <login>@dce.metz.centralesupelec.fr
```
_(Type your password)_


Start a session on a compute node:
```bash
srun -p cpu_inter --nodes=1 --time=00:30:00 --pty /bin/bash
```
- `-p cpu_inter`: the partition (group of machines) for interactive CPU sessions.
- `--time=00:30:00`: the duration of the session (here 30 minutes); auto disconnect when expires.
- `--pty /bin/bash`: gives a shell on the compute node.

Run code, e.g. `python my_script.py`.
When done, type `exit` to free the node.

```bash
squeue -u $USER    # list your running / pending jobs
scancel <jobid>    # cancel a job (e.g. a stuck session)
```