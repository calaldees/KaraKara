# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  # Tested in Vagrant 1.6.2

  config.vm.box = "trusty32"
  #config.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box"
  config.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-i386-vagrant-disk1.box"

  config.vm.provision :shell, :path => "Vagrantfile_.sh", run: "always"

  config.vm.network :forwarded_port, host:   25, guest:   25
  config.vm.network :forwarded_port, host:   80, guest:   80
  config.vm.network :forwarded_port, host: 8080, guest: 8080
  config.vm.network :forwarded_port, host: 6543, guest: 6543
  config.vm.network :forwarded_port, host: 9873, guest: 9873

  config.vm.network :private_network, ip: "10.0.0.2"
  config.vm.synced_folder ".", "/vagrant", type: "nfs"
  #sudo rm -rf /etc/exports

  config.vm.provider "virtualbox" do |v|
    #v.gui = true  # Handy for when a box is stopped without graceful shutdown
    v.name = "karakara"
    v.customize ["modifyvm", :id, "--memory", "640"]
  end

end
