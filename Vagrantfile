# -*- mode: ruby -*-
# vi: set ft=ruby :

arteriauser    = ENV['ST2USER'] ? ENV['ST2USER']: 'arteriaadmin'
arteriapasswd  = ENV['ST2PASSWORD'] ? ENV['ST2PASSWORD'] : 'arteriarulz'
st2version     = File.read('utils/st2.version.txt')

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.define "arteria" do |arteria|
    # Box details
    arteria.vm.box = "bento/ubuntu-14.04"
    arteria.vm.hostname = "arteria-dev"

    # Box Specifications
    arteria.vm.provider :virtualbox do |vb|
      vb.memory = 4048
      vb.cpus = 2
    end

    # Configure a private network
    arteria.vm.network :private_network, ip: "192.168.16.20"

    # Start shell provisioning.
    arteria.vm.provision "shell", 
      inline: "sudo apt-get update && sudo apt-get install -y curl python-virtualenv vim"

    $setup_conda = <<-SCRIPT
      wget https://repo.anaconda.com/miniconda/Miniconda2-latest-Linux-x86_64.sh && \
      bash Miniconda2-latest-Linux-x86_64.sh -b -u -p /home/vagrant/miniconda2 && \
      echo 'export PATH="/home/vagrant/miniconda2/bin:$PATH"' >> /home/vagrant/.bashrc
      SCRIPT

    arteria.vm.provision "shell", inline: $setup_conda

    arteria.vm.provision "shell", 
      inline: "curl -sSL https://stackstorm.com/packages/install.sh | bash -s -- --user=#{arteriauser} --password=#{arteriapasswd} --version=#{st2version}"

    arteria.vm.provision "shell", 
      inline: "ln -s /vagrant /opt/stackstorm/packs/snpseq_packs"

    arteria.vm.provision "shell",
      inline: "st2ctl reload"

    arteria.vm.provision "shell",
      inline: "st2 run packs.setup_virtualenv packs=snpseq_packs"
  end

end
