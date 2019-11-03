# SpecGAN - generate audio with adversarial training



Preprocess
---

At first, you need to create a .npz archive containing normalized spectrogram images of training audio files and category info. It may take a few minutes to an hour depending on the number of files in your dataset.

```
$ python preprocess_audio.py -i ./drums-selected/ -o ./training_data.npz
```


Training
---

Then, start training using the created training data!    

```
$ python specgan_categorical.py -i ./training_data.npz -o ./checkpoints -e 200
```

```
-i filepath to the training data created with proprocess_audio.py
-e number of Epochs
-o path to a directory, where the script saves generated spectrogram images, audio and models  
```
Generate Sounds
---

Once trained, you can use the trained models to generate random sounds and classify them. see [this jupyter notebook](https://github.com/nicobernasconi/specgan/blob/master/examples/generate-sound.ipynb).  



Credits 🙏
---
- The implementation of Improved Wasserstein GAN proposed in https://arxiv.org/abs/1704.00028 was based on [a keras implementation](
https://github.com/keras-team/keras-contrib/blob/master/examples/improved_wgan.py).

- Spectrogram to Audio conversion (Griffin-Lim algorithm) was based on [Yunchao He's implementation](https://github.com/candlewill/Griffin_lim).
