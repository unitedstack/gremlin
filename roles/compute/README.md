# Compute reliability verification and fault drill role

We design test cases from the following two level:

## System Level

The compute node is for running instance, which has high demands for cpu, memory, and network.

There are four key networks used by compute node:

* management
* storage
* vlan
* tunnel

### CPU

* Stress CPU load to 80% for 5 minutes
* Stress CPU load to 100% for 5 minutes

### Memory

* Stress memory load to 80% for 5 minutes
* Stress memory load to 100% for 5 minutes

### Disk

* Stress root disk util to 80% for 5 minutes
* Stress root disk util to 100% for 5 minutes

### Network

* Management network package loss to 80%
* Management network package loss to 100%
* Management network package delay to 10ms
* Management network package delay to 100ms
* Ifdown management nic

* VLAN/Tunnel network package loss to 80%
* VLAN/Tunnel network package loss to 100%
* VLAN/Tunnel network package delay to 10ms
* VLAN/Tunnel network package delay to 100ms
* VLAN/Tunnel network package delay to 200ms
* Ifdown vlan/tunnel nic

* Storage network package loss to 80%
* Storage network package loss to 100%
* Storage network package delay to 10ms
* Storage network package delay to 100ms
* Storage network package delay to 200ms
* Ifdown storage nic

## Service Level

There are following processes running on compute node:

on control plane:

* nova-compute
* neutron-openvswitch-agent
* libvirtd

on data plane:

* kvm-qemu
* ovsdb-server
* ovs-vswitchd

So we design the following test cases:

* kill nova-compute
* systemctl stop nova-compute
* kill neutron-openvswitch-agent
* systemctl stop neutron-openvswitch-agent
* kill libvirtd
* systemctl stop libvirtd
* kill a kvm/qemu process
* kill ovsdb-server
* systemctl stop ovsdb-server
* kill ovs-vswitchd
* systemctl stop ovs-vswitchd
