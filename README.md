# Gremlin

OpenStack reliability verification and fault drill system

## Background

IaaS is the cornerstone of building IT systems, the stability and reliability of
the IaaS system is critical for customers, but how to evaluate its stability and
reliability after an IaaS system has been deployed, this needs to be actually
VERIFIED, and how to quickly locate the fault when the system is in failure,
this needs to do actually FAULT DRILL. When our customers know when, how and why
the system will be in failure, and know how to handle this situation, it will be
very helpful to grow their confidence to their system.

So, we designed the OpenStack Reliability Verification and Fault Drill program,
it will do reliability verification from multiple dimensions of cloud platform,
and will introduce man-made failures by using some operation tools, thus we can
carry on fault drill along with monitoring system and logging system.

## Principle

The program should follow the principles below:

1. All faults introduced should be alerted by monitoring system.
2. All faults introduced can do fallback.
3. All faults introduced should do cleanup when a fault drill is done.


## Design

To cover more fault drill cases, the design be will formed from two aspects:

1. Horizontally, from node role, such as controller, network, compute, storage
2. Vertically, from system level, service level, and physical level

This can design a broad set of fault drill cases if combined with these two dimensions.
The test cases of system level and service level can be automated, but part of physical
level test cases should be operated by human.

## More

* Documentation: https://docs.openstack.org/gremlin
