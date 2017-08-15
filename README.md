# Gremlin

[![Build Status](https://travis-ci.org/unitedstack/gremlin.svg?branch=master)](https://travis-ci.org/unitedstack/gremlin)

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


## Usage

There are two modes when running gremlin:

* auto: All test cases will run automatically. It will introduce fault and recover
        this fault automatically. The default mode is auto.
* manual: Will run in interactive mode, when every test case is done, will prompt
          to ask if to execute the next one. And after introduced a fault, it will
          ask if to recover this fault automatically.

Before running gremlin, ensure the host running gremlin can ssh to the target hosts
without password.

Now, following the steps to get started:

1. Get the code

    ```
    git clone https://github.com/unitedstack/gremlin.git
    ```

2. Install dependencies

    ```
    ./drill.sh --install-deps
    ```

3. Define your inventory

    You should define your inventory according your environments. Modify the
    inventory/hosts file.

4. Define your configuration

    Edit the config.yml to fit your environments.

5. Run your test cases

    5.1 Run all test cases automatically:

    ```
    ./drill.sh -t all
    ```

    5.2 Run all test cases manually:

    ```
    ./drill.sh -t all --mode manual
    ```

    5.3 Run some specified test cases manually

    ```
    ./drill.sh -t mon-pre,mon-down --mode manual
    ```

6. To get more help info

    ```
    ./drill.sh -h
    ```

## More

* Documentation: https://docs.openstack.org/gremlin
