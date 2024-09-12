
const canvas = document.createElement('canvas')
const ctx = canvas.getContext('2d')

// Define the waveform gradient
const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height * 1.35)
gradient.addColorStop(0, '#656666') // Top color
gradient.addColorStop((canvas.height * 0.7) / canvas.height, '#656666') // Top color
gradient.addColorStop((canvas.height * 0.7 + 1) / canvas.height, '#ffffff') // White line
gradient.addColorStop((canvas.height * 0.7 + 2) / canvas.height, '#ffffff') // White line
gradient.addColorStop((canvas.height * 0.7 + 3) / canvas.height, '#B1B1B1') // Bottom color
gradient.addColorStop(1, '#B1B1B1') // Bottom color

// Define the progress gradient
const progressGradient = ctx.createLinearGradient(0, 0, 0, canvas.height * 1.35)
progressGradient.addColorStop(0, '#EE772F') // Top color
progressGradient.addColorStop((canvas.height * 0.7) / canvas.height, '#EB4926') // Top color
progressGradient.addColorStop((canvas.height * 0.7 + 1) / canvas.height, '#ffffff') // White line
progressGradient.addColorStop((canvas.height * 0.7 + 2) / canvas.height, '#ffffff') // White line
progressGradient.addColorStop((canvas.height * 0.7 + 3) / canvas.height, '#F6B094') // Bottom color
progressGradient.addColorStop(1, '#F6B094') // Bottom color


const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60)
    const secondsRemainder = Math.round(seconds) % 60
    const paddedSeconds = `0${secondsRemainder}`.slice(-2)
    return `${minutes}:${paddedSeconds}`
}

// Create the waveform
setsList.forEach((setObj) => {
    console.log(setObj)
    const wavesurfer = WaveSurfer.create({
        backend: 'MediaElement',
        container: `#${setObj.id}-waveform`,
        waveColor: gradient,
        progressColor: progressGradient,
        barWidth: 2,
    })
    setObj.wavesurfer = wavesurfer;
    fetch(setObj.peaks_path)
        .then(response => {
            if (!response.ok) {
                throw new Error("HTTP error " + response.status);
            }
            return response.json();
        })
        .then(peaks => {
            wavesurfer.load(setObj.path, peaks.data);
        })
        .catch((e) => {
            console.error('error', e);
        });

    // Play/pause on click
    wavesurfer.on('interaction', () => {
        setsList.forEach((setObjOther) => {
            if (setObjOther.id !== setObj.id) {
                setObjOther.wavesurfer.pause()
            }
        });
        wavesurfer.play()
    })

    const button = document.querySelector(`#${setObj.id}-button`)
    button.addEventListener('click', () => {
        setsList.forEach((setObjOther) => {
            if (setObjOther.id !== setObj.id) {
                setObjOther.wavesurfer.pause()
            }
        });
        wavesurfer.playPause()
    })

    // Hover effect
    {
        const hover = document.querySelector(`#${setObj.id}-hover`)
        const waveform = document.querySelector(`#${setObj.id}`)
        waveform.addEventListener('pointermove', (e) => (hover.style.width = `${e.offsetX}px`))
    }

    // Current time & duration
    {
        const timeEl = document.querySelector(`#${setObj.id}-time`)
        const durationEl = document.querySelector(`#${setObj.id}-duration`)
        wavesurfer.on('decode', (duration) => (durationEl.textContent = formatTime(duration)))
        wavesurfer.on('timeupdate', (currentTime) => (timeEl.textContent = formatTime(currentTime)))
    }
})
