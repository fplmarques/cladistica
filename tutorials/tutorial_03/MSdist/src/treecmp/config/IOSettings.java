/** This file is part of MSdist, a program for computing the Matching Split
    distance between phylogenetic trees.
    Copyright (C) 2010,  Damian Bogdanowicz

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>. */

package treecmp.config;


public class IOSettings {

    private static IOSettings IOConf;
    private String inputFile;
    private String outputFile;
    private String sSep;
    //defalut false
    private boolean calcCorrelation;

    public boolean isCalcCorrelation() {
        return calcCorrelation;
    }

    public void setCalcCorrelation(boolean calcCorrelation) {
        this.calcCorrelation = calcCorrelation;
    }

    private int iStep;

    public String getSSep() {
        return sSep;
    }

    public void setSSep(String sSep) {
        this.sSep = sSep;
    }

    public int getIStep() {
        return iStep;
    }

    public void setIStep(int iStep) {
        this.iStep = iStep;
    }

    public String getInputFile() {
        return inputFile;
    }

    public void setInputFile(String inputFile) {
        this.inputFile = inputFile;
    }

    public String getOutputFile() {
        return outputFile;
    }

    public void setOutputFile(String outputFile) {
        this.outputFile = outputFile;
    }
    

     protected IOSettings()
     {
         inputFile=null;
         outputFile=null;
         iStep=1;
         calcCorrelation=false;

     }
     public static IOSettings getIOSettings()
    {
        if(IOConf==null)
        {
            IOConf=new IOSettings();
        }
        return IOConf;
    }


}


