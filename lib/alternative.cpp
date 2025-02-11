#include "addm.h"
#include "util.h"
#include "stats.h"

double aDDM::getLikelihoodAlternative(aDDMTrial trial, int timeStep, float stateStep) {
    // EXAMPLE CODE!
    try {
        return 1 / this->optionalParams["W"];
    } catch (exception e) {
        return 1;
    }
}

aDDMTrial aDDM::simulateTrialAlternative(float valueLeft, float valueRight, FixationData fixationData, int timeStep, 
    int numFixDists, fixDists fixationDist, vector<int> timeBins, int seed) {

    return aDDMTrial(); 
}