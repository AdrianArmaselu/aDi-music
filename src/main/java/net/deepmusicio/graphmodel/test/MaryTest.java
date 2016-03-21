package net.deepmusicio.graphmodel.test;

import java.io.*;

import javax.sound.midi.*;

/**
 * Created by Adisor on 3/19/2016.
 */
public class MaryTest {

    public static void main(String[] args) throws MidiUnavailableException, IOException, InvalidMidiDataException {

        // Obtains the default Sequencer connected to a default device.
        Sequencer sequencer = MidiSystem.getSequencer();

        // Opens the device, indicating that it should now acquire any
        // system resources it requires and become operational.
        sequencer.open();
//        MidiUtils.getTempoMPQ();
//        MidiUtils.


        // create a stream from a file
        String fileName = "music/Eminem/thewayiam.mid";
        ClassLoader classLoader = MaryTest.class.getClassLoader();
        File file = new File(classLoader.getResource(fileName).getFile());
        InputStream is = new BufferedInputStream(new FileInputStream(file));

        // Sets the current sequence on which the sequencer operates.
        // The stream must point to MIDI file data.
        sequencer.setSequence(is);
        sequencer.getTempoInBPM();

        System.out.println(sequencer.getSequence().getDivisionType());
        System.out.println(sequencer.getSequence().getResolution());
        System.out.println(sequencer.getTempoInBPM());
        double resolution = sequencer.getSequence().getResolution();
        double tempo = sequencer.getTempoInBPM();
        double ticksPerSecond = resolution * (tempo / 60.0);
        double tickSize = 1.0 / ticksPerSecond;
        System.out.println(tickSize);

        // Starts playback of the MIDI data in the currently loaded sequence.
//        sequencer.start();
//        while(sequencer.isRecording()){
//            try {
//                Thread.sleep(1000);
//            } catch (InterruptedException e) {
//                e.printStackTrace();
//            }
//        }
        sequencer.stop();
        sequencer.close();
    }
}
