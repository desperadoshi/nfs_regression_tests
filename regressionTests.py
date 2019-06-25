#   This file is part of aither.
#   Copyright (C) 2015-18  Michael Nucci (mnucci@pm.me)
#
#   Aither is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Aither is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>. 
#
#   This script runs regression tests to test builds on linux and macOS for
#   travis ci, and windows for appveyor
#
#   Modified by Jingchang Shi for NFS.
#   2019-06-18, 21:44:43
#
import os
import optparse
import shutil
import sys
import datetime
import subprocess
import time

class regressionTest:
    def __init__(self):
        self.caseName = "none"
        self.iterations = 100
        self.procs = 1
        self.residuals = [1.0, 1.0, 1.0, 1.0, 1.0]
        self.ignoreIndices = []
        self.location = os.getcwd()
        self.runDirectory = "."
        self.nfsPath = "nfs"
        self.mpirunPath = "mpirun"
        self.percentTolerance = 0.01
        self.isRestart = False
        self.restartFile = "none"
        self.passedStatus = "none"
        self.isProfile = False

    def SetRegressionCase(self, name):
        self.caseName = name

    def SetNumberOfIterations(self, num):
        self.iterations = num

    def SetNumberOfProcessors(self, num):
        self.procs = num

    def Processors(self):
        return self.procs

    def PassedStatus(self):
        return self.passedStatus

    def SetResiduals(self, resid):
        self.residuals = resid

    def SetRunDirectory(self, path):
        self.runDirectory = path

    def SetNFSPath(self, nfs_fname):
        from os.path import join,abspath
        nfs_fpath = join(self.location, os.pardir)
        nfs_fpath = join(nfs_fpath, nfs_fname)
        self.nfsPath = abspath(nfs_fpath)

    def SetMpirunPath(self, path):
        self.mpirunPath = path

    def SetIgnoreIndices(self, ind):
        self.ignoreIndices.append(ind)

    def SetPercentTolerance(self, per):
        self.percentTolerance = per

    def GoToRunDirectory(self):
        os.chdir(self.runDirectory)

    def SetRestart(self, resFlag):
        self.isRestart = resFlag

    def SetProfile(self, profFlag):
        self.isProfile = profFlag

    def SetRestartFile(self, resFile):
        self.restartFile = resFile

    def ReturnToHomeDirectory(self):
        os.chdir(self.location)

    def GetTestCaseResiduals(self):
        fname = default_res_fname
        rfile = open(fname, "r")
        lastLine = rfile.readlines()[-1]
        rfile.close()
        tokens = lastLine.split()
        resids = [float(ii) for ii in tokens[1:1+len(self.residuals)]]
        return resids

    def CompareResiduals(self, returnCode):
        testResids = self.GetTestCaseResiduals()
        resids = []
        truthResids = []
        for ii in range(0, len(testResids)):
            if ii not in self.ignoreIndices:
                resids.append(testResids[ii])
                truthResids.append(self.residuals[ii])
        if (returnCode == 0):
            passing = [abs(resid - truthResids[ii]) <= self.percentTolerance * abs(truthResids[ii])
                       for ii, resid in enumerate(resids)]
        else:
            passing = [False for ii in resids]
        return passing, resids, truthResids

    def GetResiduals(self):
        return self.residuals
        
    # change input file to have number of iterations specified for test
    def ModifyInputFile(self):
        fname = default_input_fname
        fnameBackup = fname + ".old"
        shutil.move(fname, fnameBackup)
        with open(fname, "w") as fout:
            with open(fnameBackup, "r") as fin:
                for line in fin:
                    if "NUM_TIMESTEPS=" in line:
                        fout.write("NUM_TIMESTEPS=" + str(self.iterations) + "\n")
                    #  elif "outputFrequency:" in line:
                    #      fout.write("outputFrequency: " + str(self.iterations) + "\n")
                    #  elif "restartFrequency:" in line and self.isProfile:
                    #      fout.write("restartFrequency: " + str(self.iterations) + "\n")
                    else:
                        fout.write(line)

    # modify the input file and run the test
    def RunCase(self):
        self.GoToRunDirectory()
        print("---------- Starting Test:", self.caseName, "----------")
        print("Current directory:", os.getcwd())
        print("Modifying input file...")
        self.ModifyInputFile()
        cmd = self.mpirunPath + " -np " + str(self.procs) + " " + self.nfsPath \
            + " " + default_input_fname + " > " + self.caseName + ".out"
        print(cmd)
        start = datetime.datetime.now()
        interval = start
        process = subprocess.Popen(cmd, shell=True)
        while process.poll() is None:
            current = datetime.datetime.now()
            if (current - interval).total_seconds() > 60.:
                print("----- Run Time: %s -----" % (current - start))
                interval = current
            time.sleep(0.5)
        returnCode = process.poll()

        if (returnCode == 0):
            print("Simulation completed with no errors")
            # test residuals for pass/fail
            passed, resids, truth = self.CompareResiduals(returnCode)
            if all(passed):
                print("All tests for", self.caseName, "PASSED!")
                self.passedStatus = "PASSED"
            else:
                print("Tests for", self.caseName, "FAILED!")
                print("Residuals should be:", truth)
                print("Residuals are:", resids)
                self.passedStatus = "MISMATCH"
        else:
            print("ERROR: Simulation terminated with errors")
            self.passedStatus = "ERRORS"
        duration = datetime.datetime.now() - start

        print("Test Duration:", duration)
        print("---------- End Test:", self.caseName, "----------")
        print("")
        print("")
        self.ReturnToHomeDirectory()
        return passed

    def CleanCase(self):
        self.GoToRunDirectory()
        cmd = "rm -rf CGNS_files/ Restart_files/ residual.dat *.old *.out"
        print(cmd)
        process = subprocess.Popen(cmd, shell=True)
        #  time.sleep(0.5)
        #  out_ierr = process.poll()
        out_ierr = process.wait(timeout=1)
        self.ReturnToHomeDirectory()
        return out_ierr

# Define the test cases
default_nproc = 4
default_niter = 100
default_input_fname = "nfs.in"
default_res_fname = "residual.dat"
default_nfs_relpath = "nfs/release/bin/nfs_opt"
isProfile = False

test_case_param_list_of_dict = [
    { "name": "VortexTransport",
      "run_directory": "VortexTransport",
      "number_of_processors": default_nproc,
      "number_of_iterations": default_niter,
      "residuals": [-1.065360235E+01,-1.071742632E+01,-1.044515939E+01,-1.025530768E+01],
      "nfs_version": "37e54c6"
    }
]

n_test_case = len(test_case_param_list_of_dict)

def test_case(in_tcpd, in_totalPass, in_options):
    case = regressionTest()
    case.SetRegressionCase(in_tcpd["name"])
    case.SetNFSPath(default_nfs_relpath)
    case.SetRunDirectory(in_tcpd["run_directory"])
    case.SetProfile(isProfile)
    case.SetNumberOfProcessors(in_tcpd["number_of_processors"])
    case.SetNumberOfIterations(in_tcpd["number_of_iterations"])
    case.SetResiduals(in_tcpd["residuals"])
    case.SetIgnoreIndices([])
    case.SetMpirunPath(in_options.mpirunPath)
    # run regression case
    passed = case.RunCase()
    out_totalPass = in_totalPass and all(passed)
    out_PassedStatus = case.PassedStatus()
    if(out_PassedStatus == "PASSED"):
        CleanedErr = case.CleanCase()
        if(CleanedErr == 0):
            out_CleanedStatus = "CLEANED"
        else:
            out_CleanedStatus = "NOT_CLEANED"
    return out_PassedStatus, out_totalPass, out_CleanedStatus

def main():
    # Set up options
    parser = optparse.OptionParser()
    parser.add_option("-a", "--nfsPath", action="store", dest="nfsPath",
                      default="nfs",
                      help="Path to nfs executable. Default = nfs")
    parser.add_option("-o", "--operatingSystem", action="store",
                      dest="operatingSystem", default="linux",
                      help="Operating system that tests will run on [linux/macOS/windows]. Default = linux")
    parser.add_option("-m", "--mpirunPath", action="store",
                      dest="mpirunPath", default="mpirun",
                      help="Path to mpirun. Default = mpirun")
    parser.add_option("-b", "--build", action="store",
                      dest="build", default="release",
                      help="build type used in compilation. Default = release")

    options, remainder = parser.parse_args()

    # travis macOS images have 1 proc, ubuntu have 2
    # appveyor windows images have 2 procs
    #  maxProcs = 4

    #  isProfile = options.build == "debug"
    #  numIterations = 100
    #  numIterationsShort = 20
    #  numIterationsRestart = 50
    #  if isProfile:
    #    numIterations = 1
    #    numIterationsShort = 1
    #    numIterationsRestart = 1

    # ------------------------------------------------------------------
    #
    totalPass = True
    for i_case in range(n_test_case):
        passedStatus, totalPass, cleanedStatus = \
            test_case(test_case_param_list_of_dict[i_case], totalPass, options)
        print("%s: %s, %s"%(test_case_param_list_of_dict[i_case]["name"], \
            passedStatus, cleanedStatus))
    # ------------------------------------------------------------------
    # regression test overall pass/fail
    # ------------------------------------------------------------------
    errorCode = 0
    print("--------------------------------------------------")
    if totalPass != "ERRORS":
        print("All tests passed!")
    else:
        print("ERROR: Some tests failed")
        errorCode = 1

    if(errorCode != 0):
        sys.exit(errorCode)

    sys.exit(errorCode)

if __name__ == "__main__":
    main()
