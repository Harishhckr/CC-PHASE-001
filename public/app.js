class DJMixer {
    constructor() {
        this.initElements();
        this.initAudioContexts();
        this.initState();
        this.initEventListeners();
        this.startAnimationLoop();
    }

    initElements() {
        this.audioA = document.getElementById('audio-a');
        this.audioB = document.getElementById('audio-b');
        this.fileA = document.getElementById('file-a');
        this.fileB = document.getElementById('file-b');
        this.syncStatus = document.getElementById('sync-status');

        this.playBtnA = document.getElementById('play-a');
        this.playBtnB = document.getElementById('play-b');
        this.stopBtnA = document.getElementById('stop-a');
        this.stopBtnB = document.getElementById('stop-b');
        this.cueBtnA = document.getElementById('cue-a');
        this.cueBtnB = document.getElementById('cue-b');

        this.waveformA = document.getElementById('waveform-a');
        this.waveformB = document.getElementById('waveform-b');
        this.playheadA = document.getElementById('playhead-a');
        this.playheadB = document.getElementById('playhead-b');

        this.vuMeterA = document.getElementById('vu-meter-a');
        this.vuMeterB = document.getElementById('vu-meter-b');
        this.masterMeter = document.getElementById('master-meter');

        this.volumeA = document.getElementById('volume-a');
        this.volumeB = document.getElementById('volume-b');
        this.speedA = document.getElementById('speed-a');
        this.speedB = document.getElementById('speed-b');

        this.crossfader = document.getElementById('crossfader');
        this.masterVolume = document.getElementById('master-volume');

        this.volumeAValue = document.getElementById('volume-a-value');
        this.volumeBValue = document.getElementById('volume-b-value');
        this.speedAValue = document.getElementById('speed-a-value');
        this.speedBValue = document.getElementById('speed-b-value');
        this.masterValue = document.getElementById('master-value');

        this.timeACurrent = document.getElementById('time-a-current');
        this.timeATotal = document.getElementById('time-a-total');
        this.timeBCurrent = document.getElementById('time-b-current');
        this.timeBTotal = document.getElementById('time-b-total');

        this.trackNameA = document.querySelector('#track-a-info .track-name');
        this.trackNameB = document.querySelector('#track-b-info .track-name');

        this.deckStatusA = document.getElementById('deck-a-status');
        this.deckStatusB = document.getElementById('deck-b-status');

        this.eqHighA = document.getElementById('eq-high-a');
        this.eqMidA = document.getElementById('eq-mid-a');
        this.eqLowA = document.getElementById('eq-low-a');
        this.eqHighB = document.getElementById('eq-high-b');
        this.eqMidB = document.getElementById('eq-mid-b');
        this.eqLowB = document.getElementById('eq-low-b');

        this.effectSliders = document.querySelectorAll('.effect-slider');

        this.syncAB = document.getElementById('sync-ab');
        this.syncBA = document.getElementById('sync-ba');
    }

    initAudioContexts() {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        this.analyserA = this.audioContext.createAnalyser();
        this.analyserB = this.audioContext.createAnalyser();
        this.analyserMaster = this.audioContext.createAnalyser();

        this.analyserA.fftSize = 2048;
        this.analyserB.fftSize = 2048;
        this.analyserMaster.fftSize = 256;

        this.sourceA = null;
        this.sourceB = null;
        this.gainNodeA = this.audioContext.createGain();
        this.gainNodeB = this.audioContext.createGain();
        this.masterGain = this.audioContext.createGain();

        this.gainNodeA.connect(this.analyserA);
        this.gainNodeB.connect(this.analyserB);
        this.analyserA.connect(this.masterGain);
        this.analyserB.connect(this.masterGain);
        this.masterGain.connect(this.analyserMaster);
        this.analyserMaster.connect(this.audioContext.destination);
    }

    initState() {
        this.cuePointA = 0;
        this.cuePointB = 0;
        this.isPlayingA = false;
        this.isPlayingB = false;
    }

    initEventListeners() {
        this.fileA.addEventListener('change', (e) => this.loadTrack(e, 'a'));
        this.fileB.addEventListener('change', (e) => this.loadTrack(e, 'b'));

        this.playBtnA.addEventListener('click', () => this.togglePlay('a'));
        this.playBtnB.addEventListener('click', () => this.togglePlay('b'));
        this.stopBtnA.addEventListener('click', () => this.stop('a'));
        this.stopBtnB.addEventListener('click', () => this.stop('b'));
        this.cueBtnA.addEventListener('click', () => this.setCue('a'));
        this.cueBtnB.addEventListener('click', () => this.setCue('b'));

        this.volumeA.addEventListener('input', (e) => this.updateVolume('a', e.target.value));
        this.volumeB.addEventListener('input', (e) => this.updateVolume('b', e.target.value));
        this.speedA.addEventListener('input', (e) => this.updateSpeed('a', e.target.value));
        this.speedB.addEventListener('input', (e) => this.updateSpeed('b', e.target.value));

        this.crossfader.addEventListener('input', (e) => this.updateCrossfader(e.target.value));
        this.masterVolume.addEventListener('input', (e) => this.updateMasterVolume(e.target.value));

        this.audioA.addEventListener('loadedmetadata', () => this.onTrackLoaded('a'));
        this.audioB.addEventListener('loadedmetadata', () => this.onTrackLoaded('b'));
        this.audioA.addEventListener('timeupdate', () => this.updateTime('a'));
        this.audioB.addEventListener('timeupdate', () => this.updateTime('b'));

        this.eqHighA.addEventListener('input', () => this.updateEQ('a'));
        this.eqMidA.addEventListener('input', () => this.updateEQ('a'));
        this.eqLowA.addEventListener('input', () => this.updateEQ('a'));
        this.eqHighB.addEventListener('input', () => this.updateEQ('b'));
        this.eqMidB.addEventListener('input', () => this.updateEQ('b'));
        this.eqLowB.addEventListener('input', () => this.updateEQ('b'));

        this.effectSliders.forEach(slider => {
            slider.addEventListener('input', (e) => {
                const valueDisplay = e.target.parentElement.querySelector('.effect-value');
                if (valueDisplay) {
                    valueDisplay.textContent = e.target.value + '%';
                }
            });
        });

        this.syncAB.addEventListener('click', () => this.syncDecks('a', 'b'));
        this.syncBA.addEventListener('click', () => this.syncDecks('b', 'a'));

        this.addSliderVisualFeedback();
    }

    addSliderVisualFeedback() {
        const allSliders = document.querySelectorAll('input[type="range"]');
        allSliders.forEach(slider => {
            slider.addEventListener('input', (e) => {
                this.updateSliderProgress(e.target);
            });
            this.updateSliderProgress(slider);
        });
    }

    updateSliderProgress(slider) {
        const value = ((slider.value - slider.min) / (slider.max - slider.min)) * 100;
        const gradient = `linear-gradient(90deg,
            rgba(0, 245, 255, 0.4) 0%,
            rgba(255, 0, 255, 0.4) ${value}%,
            rgba(255, 255, 255, 0.1) ${value}%,
            rgba(255, 255, 255, 0.1) 100%)`;
        slider.style.background = gradient;
    }

    syncDecks(sourceDeck, targetDeck) {
        const sourceAudio = sourceDeck === 'a' ? this.audioA : this.audioB;
        const targetAudio = targetDeck === 'a' ? this.audioA : this.audioB;
        const sourceSpeed = sourceDeck === 'a' ? this.speedA : this.speedB;
        const targetSpeed = targetDeck === 'a' ? this.speedA : this.speedB;

        if (!sourceAudio.src || !targetAudio.src) {
            console.log('Both tracks must be loaded to sync');
            return;
        }

        targetSpeed.value = sourceSpeed.value;
        this.updateSpeed(targetDeck, sourceSpeed.value);

        if (this.syncStatus) {
            this.syncStatus.textContent = 'ON';
            this.syncStatus.style.color = '#00ff00';
            setTimeout(() => {
                this.syncStatus.textContent = 'OFF';
                this.syncStatus.style.color = '#fff';
            }, 2000);
        }

        this.showSyncAnimation(sourceDeck, targetDeck);
        console.log(`Synced deck ${targetDeck.toUpperCase()} to deck ${sourceDeck.toUpperCase()}`);
    }

    showSyncAnimation(sourceDeck, targetDeck) {
        const sourceElement = document.querySelector(`.deck-${sourceDeck}`);
        const targetElement = document.querySelector(`.deck-${targetDeck}`);

        [sourceElement, targetElement].forEach(el => {
            el.style.transform = 'scale(1.02)';
            el.style.boxShadow = '0 0 40px rgba(0, 245, 255, 0.5), 0 0 40px rgba(255, 0, 255, 0.5)';
            setTimeout(() => {
                el.style.transform = '';
                el.style.boxShadow = '';
            }, 500);
        });
    }

    loadTrack(event, deck) {
        const file = event.target.files[0];
        if (!file) return;

        const audio = deck === 'a' ? this.audioA : this.audioB;
        const trackName = deck === 'a' ? this.trackNameA : this.trackNameB;
        const deckStatus = deck === 'a' ? this.deckStatusA : this.deckStatusB;
        const deckElement = document.querySelector(`.deck-${deck}`);

        trackName.textContent = 'Loading...';
        trackName.classList.add('loading');

        const url = URL.createObjectURL(file);
        audio.src = url;

        audio.addEventListener('loadedmetadata', () => {
            trackName.classList.remove('loading');
            trackName.textContent = file.name;
            deckStatus.textContent = 'LOADED';
            deckStatus.style.background = 'rgba(255, 255, 0, 0.3)';
            deckStatus.style.borderColor = 'rgba(255, 255, 0, 0.5)';
            deckStatus.style.color = '#ffff00';

            deckElement.style.transform = 'scale(1.02)';
            setTimeout(() => {
                deckElement.style.transform = '';
            }, 300);
        }, { once: true });

        if (deck === 'a' && !this.sourceA) {
            this.sourceA = this.audioContext.createMediaElementSource(this.audioA);
            this.sourceA.connect(this.gainNodeA);
        } else if (deck === 'b' && !this.sourceB) {
            this.sourceB = this.audioContext.createMediaElementSource(this.audioB);
            this.sourceB.connect(this.gainNodeB);
        }

        console.log(`Loaded track on deck ${deck.toUpperCase()}: ${file.name}`);
    }

    onTrackLoaded(deck) {
        const audio = deck === 'a' ? this.audioA : this.audioB;
        const timeTotal = deck === 'a' ? this.timeATotal : this.timeBTotal;
        const waveform = deck === 'a' ? this.waveformA : this.waveformB;

        timeTotal.textContent = this.formatTime(audio.duration);
        this.drawWaveform(waveform, deck);
    }

    togglePlay(deck) {
        const audio = deck === 'a' ? this.audioA : this.audioB;
        const playBtn = deck === 'a' ? this.playBtnA : this.playBtnB;
        const deckStatus = deck === 'a' ? this.deckStatusA : this.deckStatusB;

        if (audio.paused) {
            audio.play();
            playBtn.classList.add('playing');
            deckStatus.textContent = 'PLAYING';
            deckStatus.style.background = 'rgba(0, 255, 0, 0.2)';
            deckStatus.style.borderColor = 'rgba(0, 255, 0, 0.4)';
            deckStatus.style.color = '#00ff00';
            if (deck === 'a') this.isPlayingA = true;
            else this.isPlayingB = true;
        } else {
            audio.pause();
            playBtn.classList.remove('playing');
            deckStatus.textContent = 'PAUSED';
            deckStatus.style.background = 'rgba(255, 255, 0, 0.2)';
            deckStatus.style.borderColor = 'rgba(255, 255, 0, 0.4)';
            deckStatus.style.color = '#ffff00';
            if (deck === 'a') this.isPlayingA = false;
            else this.isPlayingB = false;
        }
    }

    stop(deck) {
        const audio = deck === 'a' ? this.audioA : this.audioB;
        const playBtn = deck === 'a' ? this.playBtnA : this.playBtnB;
        const deckStatus = deck === 'a' ? this.deckStatusA : this.deckStatusB;

        audio.pause();
        audio.currentTime = 0;
        playBtn.classList.remove('playing');
        deckStatus.textContent = 'STOPPED';
        deckStatus.style.background = 'rgba(255, 0, 0, 0.2)';
        deckStatus.style.borderColor = 'rgba(255, 0, 0, 0.4)';
        deckStatus.style.color = '#ff0000';
        if (deck === 'a') this.isPlayingA = false;
        else this.isPlayingB = false;
    }

    setCue(deck) {
        const audio = deck === 'a' ? this.audioA : this.audioB;
        if (deck === 'a') {
            this.cuePointA = audio.currentTime;
        } else {
            this.cuePointB = audio.currentTime;
        }
        console.log(`Cue point set on deck ${deck.toUpperCase()} at ${audio.currentTime.toFixed(2)}s`);
    }

    updateVolume(deck, value) {
        const gainNode = deck === 'a' ? this.gainNodeA : this.gainNodeB;
        const valueDisplay = deck === 'a' ? this.volumeAValue : this.volumeBValue;

        gainNode.gain.value = value / 100;
        valueDisplay.textContent = value;
        this.updateCrossfader(this.crossfader.value);
    }

    updateSpeed(deck, value) {
        const audio = deck === 'a' ? this.audioA : this.audioB;
        const speedValue = deck === 'a' ? this.speedAValue : this.speedBValue;

        const playbackRate = value / 100;
        audio.playbackRate = playbackRate;
        const pitchChange = ((value - 100) / 100 * 100).toFixed(1);
        speedValue.textContent = (pitchChange >= 0 ? '+' : '') + pitchChange + '%';
    }

    updateCrossfader(value) {
        const crossfadePosition = value / 100;
        const volumeA = Math.cos(crossfadePosition * Math.PI / 2);
        const volumeB = Math.sin(crossfadePosition * Math.PI / 2);

        const baseVolumeA = this.volumeA.value / 100;
        const baseVolumeB = this.volumeB.value / 100;

        this.gainNodeA.gain.value = volumeA * baseVolumeA;
        this.gainNodeB.gain.value = volumeB * baseVolumeB;

        const deckA = document.querySelector('.deck-a');
        const deckB = document.querySelector('.deck-b');

        const opacityA = 0.7 + (volumeA * 0.3);
        const opacityB = 0.7 + (volumeB * 0.3);

        deckA.style.opacity = opacityA;
        deckB.style.opacity = opacityB;
    }

    updateMasterVolume(value) {
        this.masterGain.gain.value = value / 100;
        this.masterValue.textContent = value;
    }

    updateEQ(deck) {
        console.log(`EQ updated for deck ${deck.toUpperCase()}`);
    }

    updateTime(deck) {
        const audio = deck === 'a' ? this.audioA : this.audioB;
        const timeCurrent = deck === 'a' ? this.timeACurrent : this.timeBCurrent;
        const playhead = deck === 'a' ? this.playheadA : this.playheadB;

        timeCurrent.textContent = this.formatTime(audio.currentTime);

        if (audio.duration) {
            const progress = (audio.currentTime / audio.duration) * 100;
            playhead.style.left = progress + '%';
        }
    }

    formatTime(seconds) {
        if (isNaN(seconds)) return '0:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    drawWaveform(canvas, deck) {
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        const analyser = deck === 'a' ? this.analyserA : this.analyserB;
        const dataArray = new Uint8Array(analyser.frequencyBinCount);

        ctx.fillStyle = 'rgba(0, 0, 0, 0.9)';
        ctx.fillRect(0, 0, width, height);

        const gradient = ctx.createLinearGradient(0, height / 2, 0, 0);
        if (deck === 'a') {
            gradient.addColorStop(0, 'rgba(0, 245, 255, 0.3)');
            gradient.addColorStop(0.5, 'rgba(0, 245, 255, 0.8)');
            gradient.addColorStop(1, 'rgba(0, 245, 255, 1)');
        } else {
            gradient.addColorStop(0, 'rgba(255, 0, 255, 0.3)');
            gradient.addColorStop(0.5, 'rgba(255, 0, 255, 0.8)');
            gradient.addColorStop(1, 'rgba(255, 0, 255, 1)');
        }

        ctx.fillStyle = gradient;
        ctx.strokeStyle = deck === 'a' ? '#00f5ff' : '#ff00ff';
        ctx.lineWidth = 2;

        ctx.beginPath();
        const sliceWidth = width / dataArray.length;
        let x = 0;

        for (let i = 0; i < dataArray.length; i++) {
            const v = Math.random() * 0.6 + 0.2;
            const y = height / 2;
            const amplitude = (v - 0.5) * height;

            if (i === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y + amplitude * 0.5);
            }

            x += sliceWidth;
        }

        ctx.stroke();

        ctx.globalCompositeOperation = 'source-over';
        ctx.fillStyle = gradient;
        ctx.globalAlpha = 0.3;

        x = 0;
        ctx.beginPath();
        ctx.moveTo(0, height / 2);
        for (let i = 0; i < dataArray.length; i++) {
            const v = Math.random() * 0.6 + 0.2;
            const amplitude = (v - 0.5) * height;
            ctx.lineTo(x, height / 2 + amplitude * 0.5);
            x += sliceWidth;
        }
        ctx.lineTo(width, height / 2);
        ctx.closePath();
        ctx.fill();

        ctx.globalAlpha = 1;
        ctx.globalCompositeOperation = 'source-over';
    }

    drawVUMeter(canvas, analyser) {
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        const dataArray = new Uint8Array(analyser.frequencyBinCount);

        analyser.getByteFrequencyData(dataArray);

        const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
        const level = average / 255;

        ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
        ctx.fillRect(0, 0, width, height);

        const meterHeight = height * level;
        const gradient = ctx.createLinearGradient(0, height, 0, 0);
        gradient.addColorStop(0, '#00ff00');
        gradient.addColorStop(0.5, '#ffff00');
        gradient.addColorStop(1, '#ff0000');

        ctx.fillStyle = gradient;
        ctx.fillRect(0, height - meterHeight, width, meterHeight);
    }

    drawMasterMeter(canvas, analyser) {
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;
        const dataArray = new Uint8Array(analyser.frequencyBinCount);

        analyser.getByteFrequencyData(dataArray);

        const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
        const level = average / 255;

        ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
        ctx.fillRect(0, 0, width, height);

        const meterWidth = width * level;
        const gradient = ctx.createLinearGradient(0, 0, width, 0);
        gradient.addColorStop(0, '#00ff00');
        gradient.addColorStop(0.7, '#ffff00');
        gradient.addColorStop(1, '#ff0000');

        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, meterWidth, height);
    }

    startAnimationLoop() {
        const animate = () => {
            this.drawVUMeter(this.vuMeterA, this.analyserA);
            this.drawVUMeter(this.vuMeterB, this.analyserB);
            this.drawMasterMeter(this.masterMeter, this.analyserMaster);
            this.updateBPMDisplay();
            requestAnimationFrame(animate);
        };
        animate();
    }

    updateBPMDisplay() {
        const bpmDisplay = document.getElementById('bpm-display');
        if (this.isPlayingA || this.isPlayingB) {
            const baseBPM = 120;
            const speedA = this.speedA.value / 100;
            const speedB = this.speedB.value / 100;
            const avgSpeed = this.isPlayingA && this.isPlayingB
                ? (speedA + speedB) / 2
                : this.isPlayingA ? speedA : speedB;
            const currentBPM = Math.round(baseBPM * avgSpeed);
            bpmDisplay.textContent = currentBPM;
        }
    }

    addVisualEnhancements() {
        const buttons = document.querySelectorAll('button');
        buttons.forEach(button => {
            button.addEventListener('click', () => {
                button.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    button.style.transform = '';
                }, 100);
            });
        });

        const sliders = document.querySelectorAll('input[type="range"]');
        sliders.forEach(slider => {
            slider.addEventListener('mousedown', () => {
                slider.style.transform = 'scale(1.05)';
            });
            slider.addEventListener('mouseup', () => {
                slider.style.transform = '';
            });
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const mixer = new DJMixer();
    mixer.addVisualEnhancements();
    console.log('DJ Claude Professional Mixer initialized');
    console.log('Enhanced UI with professional visual effects active');
});
