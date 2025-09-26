// PRISM Demo: Memory Cascade Prevention
//
// Copy-paste this into your module's models/ directory and run:
//   prism demo_memory_cascade.pm -prop "P>=0.997 [F \"safe_operation\"]"
//
// This demonstrates the verification track for memory modules.

mdp

// Memory system with realistic cascade dynamics
module memory_system
    // Current memory folds (0 to 1000 safety limit)
    folds : [0..1000] init 0;

    // System health states
    healthy : bool init true;
    cascaded : bool init false;

    // Normal operation: add fold with small cascade risk
    [] healthy & folds < 950 & !cascaded ->
        0.998 : (folds'=folds+1) +
        0.002 : (healthy'=false);

    // Critical zone: higher cascade risk
    [] healthy & folds >= 950 & folds < 1000 & !cascaded ->
        0.990 : (folds'=folds+1) +
        0.010 : (cascaded'=true);

    // At limit: cascade guaranteed
    [] healthy & folds = 1000 -> (cascaded'=true);

    // Recovery from unhealthy state
    [] !healthy & !cascaded ->
        0.1 : (healthy'=true) +
        0.85 : true +  // stay unhealthy
        0.05 : (cascaded'=true);

    // Absorbing cascade state
    [] cascaded -> true;

endmodule

// Prevention system (can fail and recover)
module cascade_prevention
    active : bool init true;

    // Prevention can fail with low probability
    [] active -> 0.999 : (active'=true) + 0.001 : (active'=false);

    // Recovery from failure
    [] !active -> 0.05 : (active'=true) + 0.95 : (active'=false);

endmodule

// System composition with interaction
system "memory_with_prevention"
    memory_system || cascade_prevention
endsystem

// Rewards for analysis
rewards "memory_utilization"
    !cascaded : folds/1000;
endrewards

rewards "cascade_cost"
    cascaded : 10000;
endrewards

// Key properties to verify
label "safe_operation" = !cascaded & healthy;
label "critical_zone" = folds >= 950 & !cascaded;
label "prevention_active" = active;

// Example verification commands:
//
// 1. Primary safety (target ≥99.7%):
//    prism demo_memory_cascade.pm -prop "P>=0.997 [F \"safe_operation\"]"
//
// 2. Expected memory utilization before failure:
//    prism demo_memory_cascade.pm -prop "R{\"memory_utilization\"}=? [F cascaded]"
//
// 3. Probability of entering critical zone:
//    prism demo_memory_cascade.pm -prop "P=? [F \"critical_zone\"]"
//
// 4. Time-bounded safety (1000 steps):
//    prism demo_memory_cascade.pm -prop "P>=0.99 [G<=1000 \"safe_operation\"]"