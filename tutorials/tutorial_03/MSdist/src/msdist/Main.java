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

package msdist;

import java.io.File;
import treecmp.ResultWriter;
import treecmp.TreeReader;
import treecmp.ResultWriter;
import treecmp.TreeReader;
import treecmp.command.Command;
import treecmp.commandline.CommandLineParser;
import treecmp.common.TimeDate;
import treecmp.config.ConfigSettings;
import treecmp.config.IOSettings;
import treecmp.config.PersistentInfo;

/**
 *
 * @author Damian
 */
public class Main {

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
         //networkx test

   //     NetworkxTest.test();
        //

       String runtimePath =Main.class.getProtectionDomain().getCodeSource().getLocation().getPath();
       String conf="";

       String version=Main.class.getPackage().getImplementationVersion();

       if(version==null){
           conf=runtimePath+"../"+PersistentInfo.configFile;

       }else{
           String tempPath=runtimePath.substring(0,runtimePath.lastIndexOf("/")+1);
           conf=tempPath+PersistentInfo.configFile;
       }
       //System.out.println(conf);
       File confXmlFile=new File(conf);

        ConfigSettings config=ConfigSettings.getConfig();

        config.readConfigFromFile(confXmlFile);

        Command cmd=CommandLineParser.run(args);

        if(cmd!=null)
        {

            TreeReader reader = new TreeReader(IOSettings.getIOSettings().getInputFile());
            //scanning all content of the input file
            
            if(reader.open()==-1){
                //an error occured during reading the input file
                return;
            }
                

            System.out.println(TimeDate.now()+": Start of scanning input file: "+IOSettings.getIOSettings().getInputFile());
            int numberOfTrees=reader.scan();
            reader.close();
            System.out.println(TimeDate.now()+": End of scanning input file: "+IOSettings.getIOSettings().getInputFile());
            System.out.println(TimeDate.now()+": "+numberOfTrees+" valid trees found in file: "+IOSettings.getIOSettings().getInputFile());


            reader.setStep(IOSettings.getIOSettings().getIStep());
            cmd.setReader(reader);

            ResultWriter out = new ResultWriter();
            out.isWriteToFile(true);
            out.setFileName(IOSettings.getIOSettings().getOutputFile());
            cmd.setOut(out);

            cmd.run();


        }
    }

}
