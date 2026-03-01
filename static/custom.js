
const canvas = document.createElement('canvas')
const ctx = canvas.getContext('2d')

// Define the waveform gradient
const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height * 1.35)
gradient.addColorStop(0, '#707070') // Top color
gradient.addColorStop((canvas.height * 0.7) / canvas.height, '#707070') // Top color
gradient.addColorStop((canvas.height * 0.7 + 1) / canvas.height, '#999999') // Line
gradient.addColorStop((canvas.height * 0.7 + 2) / canvas.height, '#999999') // Line
gradient.addColorStop((canvas.height * 0.7 + 3) / canvas.height, '#808080') // Bottom color
gradient.addColorStop(1, '#808080') // Bottom color

// Define the progress gradient
const progressGradient = ctx.createLinearGradient(0, 0, 0, canvas.height * 1.35)
progressGradient.addColorStop(0, '#d0d0d0') // Top color
progressGradient.addColorStop((canvas.height * 0.7) / canvas.height, '#c0c0c0') // Top color
progressGradient.addColorStop((canvas.height * 0.7 + 1) / canvas.height, '#e0e0e0') // Accent line
progressGradient.addColorStop((canvas.height * 0.7 + 2) / canvas.height, '#e0e0e0') // Accent line
progressGradient.addColorStop((canvas.height * 0.7 + 3) / canvas.height, '#d8d8d8') // Bottom color
progressGradient.addColorStop(1, '#d8d8d8') // Bottom color


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
        barWidth: 1,
        barGap: 1.5,
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

    const updateButtonIcon = () => {
        const icon = button.querySelector('i')
        const span = button.querySelector('span')
        if (wavesurfer.isPlaying()) {
            icon.textContent = 'pause'
            span.textContent = 'PAUSE'
        } else {
            icon.textContent = 'play_arrow'
            span.textContent = 'PLAY'
        }
    }

    button.addEventListener('click', () => {
        setsList.forEach((setObjOther) => {
            if (setObjOther.id !== setObj.id) {
                setObjOther.wavesurfer.pause()
            }
        });
        wavesurfer.playPause()
        setTimeout(updateButtonIcon, 10)
    })

    wavesurfer.on('play', updateButtonIcon)
    wavesurfer.on('pause', updateButtonIcon)
    wavesurfer.on('finish', updateButtonIcon)

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

// ========== Bottom Player ==========
let lastPlayedSet = null

function getDisplayedSet() {
    // Find currently playing track
    for (let set of setsList) {
        if (set.wavesurfer.isPlaying()) {
            return set
        }
    }
    // Return last played if nothing is playing
    return lastPlayedSet
}

function updateBottomPlayer() {
    const bottomPlayer = document.getElementById('bottom-player')
    const playerTitle = document.getElementById('player-title')
    const playerArtwork = document.getElementById('player-artwork')
    const playerBtn = document.getElementById('player-btn')
    const playerTime = document.getElementById('player-time')
    const playerProgress = document.getElementById('player-progress')

    // Get the set to display
    const displayedSet = getDisplayedSet()

    if (displayedSet) {
        bottomPlayer.classList.remove('hidden')
        playerTitle.textContent = displayedSet.name || displayedSet.id
        playerArtwork.src = displayedSet.artwork_path
        playerArtwork.classList.remove('hidden')

        const current = displayedSet.wavesurfer.getCurrentTime()
        const duration = displayedSet.wavesurfer.getDuration()
        const currentMin = Math.floor(current / 60)
        const currentSec = Math.floor(current % 60)
        const durationMin = Math.floor(duration / 60)
        const durationSec = Math.floor(duration % 60)

        playerTime.textContent = `${currentMin}:${String(currentSec).padStart(2, '0')} / ${durationMin}:${String(durationSec).padStart(2, '0')}`
        playerProgress.style.width = duration > 0 ? `${(current / duration) * 100}%` : '0%'

        // Update button icon based on playing state
        playerBtn.innerHTML = displayedSet.wavesurfer.isPlaying() ? '<i class="material-icons">pause</i>' : '<i class="material-icons">play_arrow</i>'

        // Track last played
        lastPlayedSet = displayedSet
    } else {
        bottomPlayer.classList.add('hidden')
    }
}

function toggleBottomPlayer() {
    const set = getDisplayedSet()
    if (set) {
        // Pause all other tracks
        setsList.forEach((setOther) => {
            if (setOther.id !== set.id) {
                setOther.wavesurfer.pause()
            }
        })
        set.wavesurfer.playPause()
        // Update immediately to show feedback
        setTimeout(updateBottomPlayer, 10)
    }
}

// Set up button click handler - use pointer events to catch both button and icon clicks
document.getElementById('player-btn').addEventListener('pointerdown', (e) => {
    e.stopPropagation()
    toggleBottomPlayer()
})

// Set up info click handler - scroll to track
document.getElementById('player-title').addEventListener('click', (e) => {
    e.stopPropagation()
    // Find the currently playing set or the last played set
    let set = null
    for (let s of setsList) {
        if (s.wavesurfer.isPlaying()) {
            set = s
            break
        }
    }
    if (!set) set = lastPlayedSet

    if (set) {
        // Use the set ID directly as it corresponds to the div ID in the HTML
        const element = document.getElementById(set.id)
        if (element) {
            // Scroll to the element - since it's an anchor with negative top, 
            // native scrollIntoView works best to align it correctly
            element.scrollIntoView({ behavior: 'smooth' })
        }
    }
})

// Update player display on interval
setInterval(updateBottomPlayer, 100)

// Initial update when this script finishes
setTimeout(updateBottomPlayer, 100)
