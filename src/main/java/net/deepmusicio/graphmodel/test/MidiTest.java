package net.deepmusicio.graphmodel.test;

import com.sun.media.sound.StandardMidiFileReader;

import javax.sound.midi.MidiChannel;
import javax.sound.midi.MidiSystem;
import javax.sound.midi.Synthesizer;
import javax.sound.midi.spi.MidiFileReader;
import java.io.*;
import java.math.BigDecimal;
import java.util.Random;

/**
 * Created by Adisor on 3/19/2016.
 */
public class MidiTest {

    public static void main(String[] args) throws IOException {
//        StandardMidiFileReader standardMidiFileReader = new StandardMidiFileReader();
//        standardMidiFileReader.getMidiFileFormat()
        BufferedReader bufferedReader = new BufferedReader(new FileReader("pi100k.txt"));
        String rawPi = bufferedReader.readLine();
        String pi = rawPi.substring(rawPi.indexOf('.') + 1);

        try {
            Synthesizer synthesizer = MidiSystem.getSynthesizer();
            synthesizer.open();

            MidiChannel[] channels = synthesizer.getChannels();
//            Random random = new Random();
//            int i = 0;
//            int piDigitIndex = 1000;
//            System.out.println(pi.length());
//            while(i++ < 1000) {
////                int note = random.nextInt(127);
//                int piDigit = Integer.parseInt(pi.charAt(piDigitIndex++) + "");
//                int note = 64 - 2 * piDigit;
//                channels[0].noteOn(note, 64);
//                Thread.sleep(200);
//                channels[0].noteOff(note);
//                Thr ead.sleep(100);
//            }
            int note = 36;
            channels[1].noteOn(note, 127);
            channels[1].noteOn(note + 10, 127);
            Thread.sleep(1000);
            channels[1].noteOn(note + 10, 0);
            Thread.sleep(10000);

            synthesizer.close();
        } catch (Exception e)
        {
            e.printStackTrace();
        }
    }
}
