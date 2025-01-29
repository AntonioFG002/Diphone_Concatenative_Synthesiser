# Diphone_Concatenative_Synthesiser

In this project, we have implemented a concatenative synthesiser of digraphs for an artificial language ‘L’ composed of six phonemes: a vowel and six phonemes. for an artificial language ‘L’ composed of six phonemes: one vowel and six consonants.

The main objective is to develop a system that, starting from a sequence of phonemes, generates an audio file with the corresponding synthesised speech. For We have recorded an inventory of sounds, labelled the phonemes in Praat, and created a programme that created a program that concatenates these sounds in Python to produce the final audio file.

The first thing that we did in this project was the creation of the diphones, which represent the transition between two consecutive phonemes in a between two consecutive phonemes in a spoken language, which are necessary for the of the project. To do this, we had to find those diphones available in our language, which is made up of six phonemes language, which is made up of six phonemes, the vowel [a] and five consonants: [b], [f], [l], [m], [t], [s].
By following the rules and restrictions of our language we obtained the following forty-six diphones: image

Those marked in black represent those which are allowed in the L language, those in red are those which are not allowed. Once all the diphones were obtained, we audio-recorded a series of formant words with these diphones using Prat's tool. These audios are recorded in mono, 16kHz and 16 bits.
