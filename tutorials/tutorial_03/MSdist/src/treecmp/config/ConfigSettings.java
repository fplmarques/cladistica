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

import java.io.File;
import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import org.w3c.dom.*;
import org.xml.sax.SAXException;
import treecmp.metric.Metric;

public class ConfigSettings {

    private static ConfigSettings config;

    protected ConfigSettings() {
        config = null;

    }

    public static ConfigSettings getConfig() {
        if (config == null) {
            config = new ConfigSettings();

        }
        return config;
    }

    public void readConfigFromFile() {
    }

    public void readConfigFromFile(File xmlFile) {


        try {
            DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
            // Use the factory to create a builder
            DocumentBuilder builder = factory.newDocumentBuilder();
            Document doc = builder.parse(xmlFile);
            String className = "";
            String metricName = "";
            String commandLineName = "";
            String metricDesc="";

            String statisticName = "";
            String statisticDesc="";

            /**
             * Update defined metric set
             * 
             */
            DefinedMetricsSet DMset = DefinedMetricsSet.getDefinedMetricsSet();

            NodeList list = doc.getElementsByTagName("metric");
            for (int i = 0; i < list.getLength(); i++) {
                // Get element
                Element element = (Element) list.item(i);
                //System.out.println(getTextValue(element, "class"));
                className = getTextValue(element, "class");
                metricName = getTextValue(element, "name");
                commandLineName = getTextValue(element, "command_name");
                metricDesc=getTextValue(element, "description");

                if(className!=null) {
                    Class cl = Class.forName(className);
                    Metric m=(Metric) cl.newInstance();

                    m.setName(metricName);
                    m.setCommandLineName(commandLineName);
                    m.setDescription(metricDesc);
                    DMset.addMetric(m);
                }
            }

            //parse statistic section

            list = doc.getElementsByTagName("reporting");
            Element element = (Element) list.item(0);
            String sSep=getTextValue(element, "filed_separator");
            IOSettings IOs=IOSettings.getIOSettings();

            if(sSep.compareTo("tab")==0) {
                IOs.setSSep("\t");
            } else {
                IOs.setSSep(sSep);
            }
            

        } catch (SAXException ex) {
            Logger.getLogger(ConfigSettings.class.getName()).log(Level.SEVERE, null, ex);
        } catch (IOException ex) {
            Logger.getLogger(ConfigSettings.class.getName()).log(Level.SEVERE, null, ex);
        } catch (Exception ex) {
            Logger.getLogger(ConfigSettings.class.getName()).log(Level.SEVERE, null, ex);
        }

    }

    /**
     * I take a xml element and the tag name, look for the tag and get
     * the text content
     * i.e for <employee><name>John</name></employee> xml snippet if
     * the Element points to employee node and tagName is 'name' I will return John
     */
    private String getTextValue(Element ele, String tagName) {
        String textVal = null;
        NodeList nl = ele.getElementsByTagName(tagName);
        if (nl != null && nl.getLength() > 0) {
            Element el = (Element) nl.item(0);
            textVal = el.getFirstChild().getNodeValue();
            textVal=textVal.trim();
        }

        return textVal;
    }
}
