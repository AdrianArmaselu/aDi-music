;OpenMusic
;
;Copyright (C) 1997, 1998, 1999, 2000 by IRCAM-Centre Georges Pompidou, Paris, France.
;
;This program is free software; you can redistribute it and/or
;modify it under the terms of the GNU General Public License
;as published by the Free Software Foundation; either version 2
;of the License, or (at your option) any later version.
;
;See file LICENSE for further informations on licensing terms.
;
;This program is distributed in the hope that it will be useful,
;but WITHOUT ANY WARRANTY; without even the implied warranty of
;MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;GNU General Public License for more details.
;
;You should have received a copy of the GNU General Public License
;along with this program; if not, write to the Free Software
;Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
;
;Authors: Gerard Assayag and Augusto Agon

(in-package :om)

;=================================================
;Midi File Object
;=================================================

(defclass InternalMidiFile ()
  ((MidiFileName :initform nil :initarg :MidiFileName :accessor MidiFileName)
   (fileseq :initform nil :accessor fileseq)
   (tracks :initform nil :initarg :tracks :accessor tracks)
   (controllers :initform nil :initarg :controllers :accessor controllers)))

(defclass MidiFile (midi-score-element InternalMidiFile) ()
  ;;;:icon 904)
  (:documentation "
A MIDI file on your computer disk.

MidiFile is a pointer to an existing file.
I can be initialized with a pathname connected to <self> or simply by evaluating the box and choosing a file.

Midifile factories can also be obtained by dragging a MIDI file from the finder to a patch window.

Lock the box ('b') in order to keep the current pointer and not reinitialize the MidiFile.
")
  )

;;;(add-player-for-object 'midifile :midi-player)

(defmethod default-edition-params ((self midifile))
  (pairlis '(outport player)
           (list *def-midi-out* :midi-player)))

(defmethod make-one-instance ((self midifile) &rest slots-vals)
   (get-midifile))

(defmethod good-val-p? ((self midifile))
   (midifilename self))

(defmethod get-initval ((self MidiFile)) (make-instance 'midifile))

(defmethod real-dur ((self midifile)) (round (extent->ms self)))

(defmethod real-duration ((self midifile) time)
  (values time (+ time (round (extent->ms self)))))

(defmethod copy-container ((self midifile) &optional (pere ()))
  (let ((copy (make-instance 'MidiFile))
        (slots  (class-instance-slots (find-class 'simple-container))))
    (when (MidiFileName self)
      (setf (MidiFileName copy) (MidiFileName self))
      (setf (fileseq copy) (mapcar 'om-midi::copy-midi-evt (fileseq self)))
      (setf (tracks copy) (loop for track in (tracks self)
                                collect  (make-instance 'MidiTrack
                                           :midinotes  (midinotes track))))
      (setf (slot-value copy 'parent) pere)
      (loop for slot in slots
            when (not (eq (slot-definition-name slot) 'parent))
            do (setf (slot-value  copy  (slot-definition-name slot))
                     (copy-container (slot-value self  (slot-definition-name slot)) copy))))
    copy))

(defmethod execption-save-p ((self midifile)) 'midifile)

(defmethod save-exepcion ((self midifile))
  (and (MidiFileName self)
       (register-resource :midi (MidiFileName self))
       `(load-midi ,(om-save-pathname-relative (MidiFileName self)))))


;;; Maquette interface
(defmethod allowed-in-maq-p ((self MidiFile))  (good-val-p? self))
(defmethod get-obj-dur ((self MidiFile)) (extent self))
(defmethod allow-strech-p ((self MidiFile) (factor number)) nil)

(defmethod get-name ((self MidiFile))
  (or (get-filename (MidiFileName self)) ""))


;=================================================
;Midi track object
;=================================================

(defclass MidiTrack ()
  ((midinotes :initform nil :initarg :midinotes :accessor midinotes)))

;--------------------set notes to Track ------------------
(defmethod cons-midi-track ((self MidiTrack) notes)
  (setf (midinotes self) notes))


;-------------------get the notes fall in the interval (x1 x2) ------------------------------
(defmethod give-notes-in-x-range ((self MidiTrack) x1 x2)
  (let ((notes (midinotes self))
        res-notes)
    (loop while (and notes (> x1 (second (car notes)))) do
          (pop notes))
    (loop while (and notes (> x2 (second (car notes)))) do
          (push (pop notes) res-notes))
    (nreverse res-notes)))

;-------------------get the notes fall in the interval (y1 y2) ------------------------------
(defun give-notes-iny-range (notes y1 y2)
  (let (res-notes)
    (loop for note in notes do
          (when (and (>= y2 (first note)) (<= y1 (first note)))
            (push note res-notes)))
    (nreverse res-notes)))

;=================================================
; LOAD FROM FILE
;=================================================

;;; MAKE A MIDIFILE INSTANCE FROM FILE
(defun load-midifile (name)
  (let ((themidiFile (make-instance 'MidiFile))
	track-list)
    (om-print (string+ "Loading MIDI file: " (namestring name) " ..."))
    (multiple-value-bind (seq nbtracks clicks format)
        (midi-load-file (namestring name))
      ;(print (list "format" format))
      ;(print (list "clicks" clicks))

      (when (equal seq :error) (om-beep-msg (string+ "Error loading a MIDI file " (namestring name))) (om-abort))
      (setf (MidiFileName themidiFile) name)
      (when seq
       	(setf (fileseq themidiFile) (convert-tempo-info seq clicks))
	(setf track-list (make-list nbtracks :initial-element nil))


        ;;; (pitch date dur vel chan ref port)
   	(loop for note in (midievents2midilist (fileseq themidiFile))
              when (plusp (third note))  ;;; dur > 0
              do (push (list (first note) (second note) (third note) (fourth note) (fifth note)) (nth (sixth note) track-list)))
	(setf (extent themidiFile) (loop for track in track-list
                                         if track maximize (+ (third (car track)) (second (car track)))))
        (setf (Qvalue themidiFile)  1000)
        (setf (tracks themidiFile) (loop for track in track-list
                                         if track collect
                                         (make-instance 'MidiTrack :midinotes (reverse track))))
        (setf (controllers themidiFile) (get-continuous-controllers themidifile))
        themidifile))))


(defmethod get-midifile ()
            :initvals nil :indoc nil ;;;:icon 148
            (let ((name (om-choose-file-dialog
                         :directory (def-load-directory)
                         :prompt (om-str :choose-midi) :types (list (format nil (om-str :file-format) "MIDI") "*.mid;*.midi"
                                                                            (om-str :all-files) "*.*"))))
              (if name
                (progn
                  (setf *last-loaded-dir* (pathname-dir name))
                  (load-midifile name))
                (om-abort))))

(defun load-midi (name)
  (om-load-if name 'load-midifile))


;=================
; FUNCTIONS
;=================
(defmethod mf-info ((self midifile) &optional (tracknum nil))
  :initvals (list nil nil ) :indoc '("a Midifile object" "a track number or nil")
   :doc "Converts a Midifile object into a symbolic description.
The result of mf-info is a list of tracks. Each track is a list of notes.
Each note is a list of parameters in the form :

(midi-number (pitch) , onset-time(ms), duration(ms), velocity, channel)

optional <tracknum> (a number in 0-15) allows to choose a single track."
  ;;;;;;:icon 148
  (if tracknum
    (midinotes (nth tracknum (tracks self)))
    (loop for item in (tracks self)
          collect (midinotes item))))

(defmethod mf-info-mc ((self midifile) &optional (tracknum nil))
            :initvals (list nil nil ) :indoc '("a Midifile object" "a track number or nil")
            :doc "Converts a Midifile object into a symbolic description.
The result of mf-info is a list of tracks. Each track is a list of notes.
Each note is a list of parameters in the form :

(midi-number (pitch) , onset-time(ms), duration(ms), velocity, channel)

optional <tracknum> (a number in 0-15) allows to choose a single track."
            ;;;;;;:icon 148
            (if tracknum
                (midinotes (nth tracknum (tracks self)))
              (loop for item in (tracks self)
                    collect (midinotes item))))


;=== Creates MidiEvent list with all Midi events
;=== optionnaly filtered with a test function

(defmethod get-midievents ((self midifile) &optional test)
  :initvals '(nil nil)
  :indoc '("an OM object" "a test function")
  :doc "
Converts any OM object (<self>) to a list of MIDIEvents.

The optional argument <test> is a function or lambda patch testing MIDIEvents one by one.
If <test> returns T, then the MIDIEvent is collected.
"
  ;;;;;;:icon 902
   (remove nil
           (loop for e in (fileseq self) collect
                 (let ((event (make-instance 'MidiEvent
                                            :ev-date (om-midi::midi-evt-date e)
                                            :ev-type (om-midi::midi-evt-type e)
                                            :ev-chan (om-midi::midi-evt-chan e)
                                            :ev-ref (om-midi::midi-evt-ref e)
                                            :ev-port (om-midi::midi-evt-port e)
                                            :ev-fields (if (equal (om-midi::midi-evt-type e) :Tempo)
                                                           (list (mstempo2bpm (om-midi::midi-evt-tempo e)))
                                                         (om-midi::midi-evt-fields e))
                                            )))
                   (when (or (not test) (funcall test event))
                     event))

                 )))



;=== Creates a string with Lyric events from Midi file

(defmethod get-mf-lyrics ((self midifile))
  :initvals '(nil)
  :indoc '("a MIDI file or sequence")
  :numouts 2
  :doc "Extracts lyrics (event type 'Lyric') from <self>.

The second output returns the corresponding dates"
  ;;;;;;:icon '(908)
  (let ((rep
         (mat-trans (loop for evt in (fileseq self)
                          when (equal (om-midi::midi-evt-type evt) :Lyric)
                          collect (list (if (stringp (car (om-midi::midi-evt-fields evt))) (om-midi::midi-evt-fields evt) (list2string (om-midi::midi-evt-fields evt)))
                                        (om-midi::midi-evt-date evt)))
                    )))
    (values (car rep) (cadr rep))))


(defmethod get-midi-notes ((self midifile))
  :initvals '(nil)
  :indoc '("a MIDI file or sequence")
  :doc "Extracts and returns the notes from <self>.

The result is a list of lists where each first level list represents a MIDI track and contains a list of note values.
Note values are lists of (pitch date dur vel chan).

"
  ;;;:icon 909
  (mf-info self))



;=====================
; MIDIFILE BOX
;=====================

(defclass OMMidiFilebox (OMBoxEditCall) ())

(defmethod get-type-of-ed-box ((self MidiFile))  'OMMidiFilebox)
(defmethod default-obj-box-size ((self MidiFile)) (om-make-point 50 72))
(defmethod get-frame-class ((self OMMidiFilebox)) 'boxmidiframe)

(defclass boxmidiframe (boxEditorFrame) ())

;(defmethod om-get-menu-context ((object boxmidiframe))
;  (boxframe-default-list object))

;(defmethod remove-extra ((self OMPatch) (box OMMidiFilebox))
;   (when (and (value box) (fileseq (value box)))
;      (om-midi-free-seq (fileseq (value box)))))


;(defun copy-midiseq-without-tempoevents (seq)
;   (om-midi-copy-seq seq '(:type 144)))

;ojo deberia ser standard
;notalist (midi ? vel ? ttime ?)

(defmethod get-obj-from-file ((type (eql 'mid)) filename)
  (load-midifile filename))
(defmethod get-obj-from-file ((type (eql 'midi)) filename)
  (load-midifile filename))