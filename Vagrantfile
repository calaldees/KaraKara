# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "precise32"

  config.vm.provision :shell, :path => "vagrant_bootstrap.sh"

  config.vm.provider "virtualbox" do |v|
    v.name = "karakara"
    v.customize ["modifyvm", :id, "--memory", "512"]
  end

end
