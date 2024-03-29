#!/usr/bin/env python

import argparse
import rospy

from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *
import pyaudio

from std_msgs.msg import String
from std_srvs.srv import *
import os
import commands

class recognizer(object):

    def __init__(self):

        # initialize ROS
        self.speed = 0.2

        # Start node
        rospy.init_node("recognizer")
        rospy.on_shutdown(self.shutdown)

        self._lm_param = "~lm"
        self._dict_param = "~dict"
        self._kws_param = "~kws"
        self._stream_param = "~stream"
        self._wavpath_param = "~wavpath"

        # you may need to change publisher destination depending on what you run
        self.pub_ = rospy.Publisher('kws_data', String, queue_size=1)

        if rospy.has_param(self._lm_param):
            self.lm = rospy.get_param(self._lm_param)
        else:
            rospy.loginfo("Loading the default acoustic model")
	    self.lm = "/home/deep/catkin_ws/src/pocketsphinx/model_adaption/eng_ind"
            #self.lm = "/home/deep/Downloads/hub4wsj_sc_8k"
            rospy.loginfo("Done loading the default acoustic model")

        if rospy.has_param(self._dict_param):
            self.lexicon = rospy.get_param(self._dict_param)
        else:
            rospy.logerr('No dictionary found. Please add an appropriate dictionary argument.')
            return

        if rospy.has_param(self._kws_param):
            self.kw_list = rospy.get_param(self._kws_param)
        else:
            rospy.logerr('kws cant run. Please add an appropriate keyword list file.')
            return

        if rospy.has_param(self._stream_param):
            self.is_stream = rospy.get_param(self._stream_param)
            if not self.is_stream:
                if rospy.has_param(self._wavpath_param):
                    self.wavpath = rospy.get_param(self._wavpath_param)
                    if self.wavpath == "none":
                        rospy.logerr('Please set the wav path to the correct file location')
                else:
                    rospy.logerr('No wav file is set')
        else:
            rospy.logerr('Audio is not set to a stream (true) or wav file (false).')
            self.is_stream = rospy.get_param(self._stream_param)

        self.start_recognizer()

    def start_recognizer(self):
        # initialize pocketsphinx. As mentioned in python wrapper
        rospy.loginfo("Initializing pocketsphinx")
        config = Decoder.default_config()
        rospy.loginfo("Done initializing pocketsphinx")

        # Hidden Markov model: The model which has been used
        config.set_string('-hmm', self.lm)
        # Pronunciation dictionary used
        config.set_string('-dict', self.lexicon)
        # Keyword list file for keyword searching
        config.set_string('-kws', self.kw_list)

        rospy.loginfo("Opening the audio channel")

        if not self.is_stream:
            self.decoder = Decoder(config)
            self.decoder.start_utt()
            try:
                wavFile = open(self.wavpath, 'rb')
            except:
                rospy.logerr('Please set the wav path to the correct location from the pocketsphinx launch file')
                rospy.signal_shutdown()
            # Update the file link above with relevant username and file
            # location
            in_speech_bf = False
            while not rospy.is_shutdown():
                buf = wavFile.read(1024)
                if buf:
                    self.decoder.process_raw(buf, False, False)
                else:
                    break
            self.decoder.end_utt()
            hypothesis = self.decoder.hyp()
            if hypothesis == None:
                rospy.logwarn("Error, make sure your wav file is composed of keywords!!")
                rospy.logwarn("Otherwise, your speech is uninterpretable :C ")
            else:
                print "\n",hypothesis.hypstr,"\n"

        else:
            stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1,
                        rate=16000, input=True, frames_per_buffer=32)
            stream.start_stream()
            rospy.loginfo("Done opening the audio channel")

            #decoder streaming data
            rospy.loginfo("Starting the decoder")
            self.decoder = Decoder(config)
            self.decoder.start_utt()
            rospy.loginfo("Done starting the decoder")

            # Main loop
            while not rospy.is_shutdown():
                # taken as is from python wrapper
                buf = stream.read(1024)
                if buf:
                    self.decoder.process_raw(buf, False, False)
                else:
                    break
                self.publish_result()

    def publish_result(self):
        if self.decoder.hyp() != None:
            print("\n")
            print ([(seg.word) 
                for seg in self.decoder.seg()])
	    print("\n")
            seg.word = seg.word.lower()
            self.decoder.end_utt()
            self.decoder.start_utt()
            self.pub_.publish(seg.word)

    def shutdown(self):
        rospy.loginfo("Stopping PocketSphinx")

if __name__ == "__main__":
    if len(sys.argv) > 0:
        start = recognizer()
