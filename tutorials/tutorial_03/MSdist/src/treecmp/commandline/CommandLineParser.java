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

package treecmp.commandline;

import java.util.Comparator;
import java.util.Hashtable;
import java.util.ListIterator;
import java.util.Vector;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.GnuParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.OptionGroup;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;
import treecmp.config.*;
import treecmp.metric.Metric;
import treecmp.command.*;

public class CommandLineParser {

    private final static String S_DESC = "- Pair comparison mode. Every two neighbouring trees are compared.";
    private final static String W_DESC = "- Window comparison mode. Every two trees within a window are compared.";
    private final static String M_DESC = "- Matrix comparison mode. Every two trees in the input files are compared.";
    private final static String I_DESC = "- Input file.";
    private final static String O_DESC = "- Output file.\n";
    private final static String CMD_ERROR = "Error. There is a problem with parsing the command line. See the usage below.\n";

    private final static String HEADER = "";
    //private final static String FOOTER = "ssd";
    private final static String CMD_LINE_SYNTAX = "java -jar MSdist.jar -s|-w <size>|-m -i <inputFile> -o <outputFile>\n";

    public static Command run(String args[]) {
        Command cmd = null;


        Option oS = new Option("s", S_DESC);
        Option oW = new Option("w", W_DESC);
        Option oM = new Option("m", M_DESC);
        oW.setArgName("size");
        oW.setArgs(1);
        OptionGroup cmdOpts = new OptionGroup();
        cmdOpts.addOption(oS);
        cmdOpts.addOption(oW);
        cmdOpts.addOption(oM);
        cmdOpts.setRequired(true);
        Option oI = new Option("i", I_DESC);
        oI.setArgName("inputfile");
        oI.setArgs(1);
        oI.setRequired(true);
        Option oO = new Option("o", O_DESC);
        oO.setArgs(1);
        oO.setArgName("outputfile");
        oO.setRequired(true);
        Options opts = new Options();
        opts.addOptionGroup(cmdOpts);
        opts.addOption(oI);
        opts.addOption(oO);

        DefinedMetricsSet DMSet = DefinedMetricsSet.getDefinedMetricsSet();
        Vector<Metric> DMetrics = DMSet.getDefinedMetrics();

        //getting version from manifest file
        String version = CommandLineParser.class.getPackage().getImplementationVersion();
        if (version == null) {
            version = "";
        }
        //String HEADER="MSdist version "+version;
         String FOOTER = "MSdist version "+version;

        GnuParser parser = new GnuParser();
        HelpFormatter formatter = new HelpFormatter();
        formatter.setOptionComparator(new OptOrder());
        try {
            //parser.checkRequiredOptions();

            CommandLine commandLine = parser.parse(opts, args);
            if (commandLine != null) {
                // process these values
                //set IO settings
                String inputFileName = (String) commandLine.getOptionValue(oI.getOpt());
                String outputFileName = (String) commandLine.getOptionValue(oO.getOpt());

                if(inputFileName==null){
                     System.out.println("Error: input file not specified!");
                    formatter.printHelp(CMD_LINE_SYNTAX, HEADER,opts,FOOTER, false);

                    return null;
                }
                if(outputFileName==null){
                    System.out.println("Error: output file not specified!");
                    formatter.printHelp(CMD_LINE_SYNTAX, HEADER,opts,FOOTER, false);
                    return null;
                }


                IOSettings IOset = IOSettings.getIOSettings();
                IOset.setInputFile(inputFileName);
                IOset.setOutputFile(outputFileName);


                /*
                if(commandLine.hasOption(oStep))
                {
                String sStep=(String)commandLine.getValue(oStep);
                int iStep=Integer.parseInt(sStep);
                IOset.setIStep(iStep);
                }
                 */
                //set active metrics
                ActiveMetricsSet AMSet = ActiveMetricsSet.getActiveMetricsSet();
                DMSet = DefinedMetricsSet.getDefinedMetricsSet();
                DMetrics = DMSet.getDefinedMetrics();
                ListIterator<Metric> itDM = DMetrics.listIterator();
                while (itDM.hasNext()) {
                    Metric m = itDM.next();
                    AMSet.addMetric(m);
                }
                //set active command

                if (commandLine.hasOption(oW.getOpt())) {
                    String sWindowSize = (String) commandLine.getOptionValue(oW.getOpt());
                    //String sWindowSize2 = (String) commandLine.getOptionValue();
                    int iWindowSize = Integer.parseInt(sWindowSize);
                    cmd = new RunWCommand(1, "-w", iWindowSize);
                }
                if (commandLine.hasOption(oM.getOpt())) {
                    cmd = new RunMCommand(0, "-m");
                }
                if (commandLine.hasOption(oS.getOpt())) {
                    cmd = new RunSCommand(0, "-s");
                }
                return cmd;
            } else {
                //Error during parsing command line
                return null;
            }
        } catch (ParseException ex) {
            System.out.println(CMD_ERROR);
            //System.out.println(ex.getMessage());
           
            formatter.printHelp(CMD_LINE_SYNTAX, HEADER,opts,FOOTER, false);

        } catch (NumberFormatException ex){
              System.out.print("Error: ");
              System.out.println("window size should be an integer.");
            formatter.printHelp(CMD_LINE_SYNTAX, HEADER,opts,FOOTER, false);


        }
        return cmd;
    }
}

class OptOrder implements Comparator {

    private Hashtable order = new Hashtable();

    public OptOrder() {
        order.put("s", new Integer(1));
        order.put("w", new Integer(2));
        order.put("m", new Integer(3));
        order.put("i", new Integer(4));
        order.put("o", new Integer(5));
    }

    public int compare(Object o1, Object o2) {
        Option opt1 = (Option) o1;
        Option opt2 = (Option) o2;
        Integer n1 = (Integer) order.get(opt1.getOpt());
        Integer n2 = (Integer) order.get(opt2.getOpt());
        if (n1 != null || n2 != null) {
            return n1 - n2;
        } else {
            return 0;
        }
    }
}
