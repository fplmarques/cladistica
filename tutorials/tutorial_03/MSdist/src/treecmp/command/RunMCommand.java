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

package treecmp.command;

import treecmp.common.ProgressIndicator;
import treecmp.common.StatCalculator;
import treecmp.common.SummaryStatCalculator;
import java.util.Vector;
import pal.tree.Tree;
import treecmp.ResultWriter;
import treecmp.TreeReader;
import treecmp.config.ActiveMetricsSet;
import treecmp.config.IOSettings;
import treecmp.metric.Metric;

public class RunMCommand extends Command {

    public RunMCommand(int paramNumber, String name) {
        super(paramNumber, name);
    }

    @Override
    public void run() {
        super.run();
        
        out.init();
        reader.open();
        
        matrixCompareExecute(reader, out);
        
        reader.close();
        out.close();
        
        
        
        
    }

    private void matrixCompareEx(TreeReader reader, ResultWriter out, Metric[] metrics) {

        pal.tree.Tree tree1,tree2 ;
        Vector<Tree> tree_vec = new Vector<Tree>();
        int k,counter,maxIt;
        double val;
        String row;


        int mSize=metrics.length;

        //initialize summary stat calculators
        SummaryStatCalculator[] sStatCalc=new SummaryStatCalculator[mSize];
        for(int i=0;i<mSize;i++)
        {
            sStatCalc[i]=new SummaryStatCalculator(metrics[i]);
        }


         String separator=IOSettings.getIOSettings().getSSep();

        String head = this.createHeader(metrics);
        out.setText(head);
        out.write();

        while ((tree1 = reader.readNextUnrootedTree()) != null) {
            tree_vec.add(tree1);
        }

        int N = tree_vec.size();
        counter=1;
        maxIt=N*(N-1)/2;
        ProgressIndicator progress=new ProgressIndicator();


        progress.setMaxVal(maxIt);
        progress.setPrintInterval(600);
        progress.setPrintPercentInterval(5.0);

        progress.init();


        for (int i = 0; i < N; i++) {
            for (int j = i + 1; j < N; j++) {

                tree1 = tree_vec.get(i);
                tree2 = tree_vec.get(j);                
                row=""+counter+separator+i+separator+j+separator;
                for(k=0;k<metrics.length-1;k++){
                    
                    val=metrics[k].getDistance(tree1, tree2);

                    row+=val+separator;
                    sStatCalc[k].insertValue(val);
                }   

                k=metrics.length-1;

                if(k>=0)
                {
                    val=metrics[k].getDistance(tree1, tree2);
                    row+=val;

                    //summary
                    sStatCalc[k].insertValue(val);
                }

                out.setText(row);
                out.write();


                progress.displayProgress(counter);
                counter++;

            }
        }

        SummaryStatCalculator.printSummary(out, sStatCalc);


    }  
    
    public void matrixCompareExecute(TreeReader reader, ResultWriter out ) {

      

        Metric[] metrics=ActiveMetricsSet.getActiveMetricsSet().getActiveMetricsTable();


        StatCalculator[] statsMetrics=new StatCalculator[metrics.length];

        for(int i=0;i<metrics.length;i++)
        {
           
            
            statsMetrics[i]=new StatCalculator(metrics[i]);


            if(IOSettings.getIOSettings().isCalcCorrelation())//temprary set statcalc to hold valuse
                statsMetrics[i].setRecordValues(true);
        }


        matrixCompareEx(reader, out, statsMetrics);

    }
    
    private String createHeader(Metric[] metrics) {


         String header = "";
         String metricName="";
         String separator=IOSettings.getIOSettings().getSSep();
         int i;

         for (i = 0; i < metrics.length-1; i++) {
             metricName=metrics[i].getName();

             header+=metricName+separator;

         }

         i=metrics.length-1;

         if(i>=0)
         {
            metricName=metrics[i].getName();
            header+=metricName;
         }

         header="state"+separator+"tree1"+separator+"tree2"+separator+header;

     return header;
    }
}
