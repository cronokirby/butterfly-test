# butterfly-test

A little test script, and implementation of a greedy algorithm for creating
Benes (double butterfly) sorting networks.

These are a way to encode permutations using a fixed topology of switches.
Each switch has two inputs and two outputs, and either swaps them,
or lets them pass through.
This provides a way to encode that the input and output values are
permutations of each other, using a boolean circuit with a fixed topology,
just with variable switch values.

This is *very* useful for ZK proofs, when compiling random access machines
to circuits.
It's much easier to prove the integrity of memory accesses if these accesses
or sorted by address.
This can be done outside of the circuit, but the circuit needs to attest
that the address sorted accesses are a permutation of the time sorted
addresses.
Using a routing network allows doing this with a fixed circuit, but
with private inputs for the switch values.
