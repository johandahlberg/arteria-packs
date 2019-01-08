# snpseq_packs

StackStorm pack to setup automation workflow taking data from the sequencer to delivery on the remote host.

## Usage

Here we describe the common use cases of: authenticating with StackStorm, running a workflow and tracking runfolders.

### Getting an authentication token

Get your auth token setup (substitute for correct user and password as necessary) :

    export ST2_AUTH_TOKEN=$(st2 auth --only-token arteriaadmin -p arteriarulz)
    
### Starting a workflow

Now you should be good to go. Here's an example of how to run a action:

     st2 run snpseq_packs.ngi_uu_workflow runfolder=/data/testarteria1/150605_M00485_0183_000000000-ABGT6_testbio14 host=testarteria1
     
To see the result of a run - you can first list the executions:

    st2 execution list
    
Pick the one you're interested in and:

    st2 execution get --detail --json <your execution id>
    
### Using traces to track a runfolder

Each execution will get its own unique id when run by StackStorm. However it can be convenient to be able to tag executions
in other ways, such as being able to see all executions for a particular runfolder. You can achieve this by
 using  the `--trace-tag` argument when staring a job, e.g:
 
    st2 run snpseq_packs.ngi_uu_workflow \
        runfolder=/data/testarteria1/150605_M00485_0183_000000000-ABGT6_testbio14 \
        host=testarteria1 \
        --trace-tag 150605_M00485_0183_000000000-ABGT6_testbio14
    
Now you can search for the trace-tag using:

    st2 trace list --trace-tag 150605_M00485_0183_000000000-ABGT6_testbio14
    
To find more information about a particular trace, use:

    st2 trace get <trace id>
    
From there you can go to getting more information on the executions using:

    st2 execution get <execution id>
       
This will list all executions and triggers associated with the tag.

All of this has been wrapped by `scripts/trace_runfolder.py`, which allows you to get all excutions of a workflow
associated with a tag, e.g.:

    python scripts/trace_runfolder.py --tag 150605_M00485_0183_000000000-ABGT6_testbio14 | xargs -n1 st2 execution get
    
For automatic triggering the trace tag can be injected via the sensor. For more info on traces, see: https://docs.stackstorm.com/reference/traces.html

## Development and testing

Here we describe how to run snpseq_packs on Vagrant, and show examples of some common testing scenarios.

### Vagrant box
To make development and testing of snpseq_packs simpler, we provide a Vagrant environment (this requires that VirtualBox is installed on your system).

```
# Get it up and running
vagrant up

# SSH into the vagrant environment
vagrant ssh

# Then go to the vagrant synced folder which contains this code
cd /vagrant

# Now you can start developing on the packs

# Note that all the scripts run below this point assume that your current
# working directory is the packs directory i.e. /vagrant in
# the vagrant environment

# Create the conda environment you need to run the tests
conda create -p ./venv python=2

# Activate the virtual environment
source activate ./venv

# Prepare the test environment with
./utils/prepare_test_env.sh

# Run the tests using the provided utility script
st2-run-pack-tests -p /opt/stackstorm/packs/snpseq_packs

```

### Configuration

You will also need to edit the configuration file on your Vagrant box at `/opt/stackstorm/configs/snpseq_packs.yaml`. The easiest way to obtain sensible values is to copy the configuration file that exists at that path on the staging machine. After editing the file, run `sudo st2ctl reload --register-configs`.

### Running services locally

Services in our production and staging environments are typically restricted to specific IP addresses. Therefore, if you wish to test a workflow from start to finish, you may have to check out and run the relevant service(s) on your local (host) machine. 

You can then make the port available to the snpseq_packs Vagrant machine using port forwarding. For example, if your host machine is running a web service on port 8080, you can let Vagrant know about it with:

`vagrant ssh -- -R 8080:localhost:8080`

Don't forget to update the config file, specifying local url's for the relevant web services, and to restart st2ctl.

### Testing Delivery Workflow

To test the delivery workflow, you will need:
- a directory containing the project to be delivered, on the machine running the arteria-delivery service
- a CSV file mapping the project name to an email addresses, on the machine running snpseq_packs

To create the latter, copy `project_email.example.csv` and edit. Ensure that the email address you use is registered with [SUPR's test environment](https://disposer.c3se.chalmers.se/supr-test/).

Then run with the following flags to skip unnecessary integrations:

    st2 run snpseq_packs.delivery_project_workflow \
        project_name=YOUR_PROJECT_NAME \
        projects_pi_email_file=/vagrant/project_email.csv \
        set_delivery_status_in_charon=False \
        skip_mover=True \
        --trace-tag YOUR_TRACE_TAG