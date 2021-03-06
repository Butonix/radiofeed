import { Controller } from 'stimulus';
import useTurbo from '../turbo';

export default class extends Controller {
  audio: HTMLMediaElement;
  audioListeners: any;

  timeupdateTimer: ReturnType<typeof setTimeout>;

  activeClass: string;
  inactiveClass: string;

  csrfTokenValue: string;
  currentTimeValue: number;
  durationValue: number;
  mediaUrlValue: string;
  metadataValue: any;
  pausedValue: boolean;
  playbackRateValue: number;
  timeupdateUrlValue: string;
  waitingValue: boolean;

  hasCounterTarget: boolean;
  hasIndicatorTarget: boolean;
  hasPlaybackRateTarget: boolean;
  hasPlayButtonTarget: boolean;
  hasPauseButtonTarget: boolean;

  counterTarget: HTMLElement;
  indicatorTarget: HTMLElement;
  pauseButtonTarget: HTMLElement;
  playButtonTarget: HTMLElement;
  playbackRateTarget: HTMLElement;
  playNextTarget: HTMLFormElement;
  progressBarTarget: HTMLElement;

  static targets: string[] = [
    'audio',
    'controls',
    'counter',
    'indicator',
    'pauseButton',
    'playbackRate',
    'playButton',
    'playNext',
    'progressBar',
    'stop',
  ];

  static classes: string[] = ['active', 'inactive'];

  static values: any = {
    csrfToken: String,
    currentTime: Number,
    duration: Number,
    mediaUrl: String,
    metadata: Object,
    paused: Boolean,
    playbackRate: Number,
    timeupdateUrl: String,
    waiting: Boolean,
  };

  // events

  async initialize() {
    // Audio object is used instead of <audio> element to prevent resets
    // and skips with page transitions
    //
    this.initAudio();

    this.playbackRateValue = this.playbackRateValue || 1.0;

    this.audio.currentTime = this.currentTimeValue;
    this.audio.src = this.mediaUrlValue;

    this.pausedValue = !this.enabled;

    if (this.audio && this.mediaUrlValue) {
      if (this.pausedValue) {
        this.pause();
      } else {
        this.play();
      }
    }
  }

  connect() {
    useTurbo(this);
  }

  ended() {
    this.cancelTimeUpdateTimer();
    console.log('ENDED');
    this.playNextTarget.requestSubmit();
  }

  closePlayer() {
    this.durationValue = 0;
    this.mediaUrlValue = '';
    this.closeAudio();
    this.cancelTimeUpdateTimer();
  }

  loadedMetaData() {
    this.durationValue = this.audio.duration;
  }

  async play() {
    try {
      await this.audio.play();
    } catch (e) {
      console.error(e);
      this.pausedValue = true;
    }
  }

  pause() {
    this.audio.pause();
  }

  resumed() {
    this.enabled = true;
    this.pausedValue = false;
    this.waitingValue = false;
  }

  paused() {
    this.enabled = false;
    this.pausedValue = true;
  }

  wait() {
    this.waitingValue = true;
  }

  canPlay() {
    this.waitingValue = false;
  }

  timeUpdate() {
    // playing time update
    const { currentTime } = this.audio;
    this.currentTimeValue = currentTime;
    this.waitingValue = false;
  }

  incrementPlaybackRate() {
    this.changePlaybackRate(0.1);
  }

  decrementPlaybackRate() {
    this.changePlaybackRate(-0.1);
  }

  skip(event: MouseEvent) {
    // user clicks on progress bar
    const position: number = this.calcEventPosition(event.clientX);
    if (!isNaN(position) && position > -1) {
      this.skipTo(position);
    }
  }

  skipBack() {
    this.skipTo(this.audio.currentTime - 10);
  }

  skipForward() {
    this.skipTo(this.audio.currentTime + 10);
  }

  turboSubmitEnd(event: CustomEvent) {
    console.log('turboSubmitEnd');
    const { fetchResponse } = event.detail;
    const headers = fetchResponse.response ? fetchResponse.response.headers : null;
    if (!headers || !headers.has('X-Player')) {
      return;
    }
    const { action, mediaUrl, currentTime, metadata } = JSON.parse(
      headers.get('X-Player')
    );
    console.log('ACTION', action);
    if (action === 'stop') {
      console.log('close player');
      this.closePlayer();
      return;
    }
    // default : play
    //
    this.mediaUrlValue = mediaUrl;
    this.currentTimeValue = parseFloat(currentTime || 0);

    console.log('metadata', metadata);
    if (metadata) {
      this.metadataValue = metadata;
    }

    this.initAudio();

    this.audio.src = this.mediaUrlValue;
    this.audio.currentTime = this.currentTimeValue;

    this.play();

    console.log('play:', mediaUrl, currentTime);
  }

  // observers
  pausedValueChanged() {
    if (this.hasPauseButtonTarget && this.hasPlayButtonTarget) {
      if (this.pausedValue) {
        this.pauseButtonTarget.classList.add('hidden');
        this.playButtonTarget.classList.remove('hidden');
      } else {
        this.pauseButtonTarget.classList.remove('hidden');
        this.playButtonTarget.classList.add('hidden');
      }
    }
    this.toggleActiveMode();
  }

  waitingValueChanged() {
    this.toggleActiveMode();
  }

  durationValueChanged() {
    this.updateCounter(this.durationValue);
    this.updateProgressBar();
  }

  currentTimeValueChanged() {
    this.updateCounter(this.durationValue - this.currentTimeValue);
    this.updateProgressBar();
  }

  playbackRateValueChanged() {
    if (this.audio) {
      this.audio.playbackRate = this.playbackRateValue;
    }
    if (this.hasPlaybackRateTarget) {
      this.playbackRateTarget.textContent = this.playbackRateValue.toFixed(1) + 'x';
    }
  }

  metadataValueChanged() {
    if ('mediaSession' in navigator && this.metadataValue) {
      // @ts-ignore
      navigator.mediaSession.metadata = new window.MediaMetadata(this.metadataValue);
    }
  }

  changePlaybackRate(increment: number) {
    let newValue = this.playbackRateValue + increment;
    if (newValue > 2.0) {
      newValue = 2.0;
    } else if (newValue < 0.5) {
      newValue = 0.5;
    }
    this.playbackRateValue = newValue;
  }

  updateProgressBar() {
    if (this.hasIndicatorTarget) {
      const pcComplete = this.calcPercentComplete();
      this.indicatorTarget.style.left =
        this.calcCurrentIndicatorPosition(pcComplete) + 'px';
    }
  }

  updateCounter(value: number) {
    if (this.hasCounterTarget) {
      this.counterTarget.textContent = this.formatTimeRemaining(value);
    }
  }

  calcPercentComplete(): number {
    if (!this.currentTimeValue || !this.durationValue) {
      return 0;
    }

    if (this.currentTimeValue > this.durationValue) {
      return 100;
    }

    return (this.currentTimeValue / this.durationValue) * 100;
  }

  calcEventPosition(clientX: number): number {
    if (!isNaN(clientX)) {
      const { left } = this.progressBarTarget.getBoundingClientRect();
      const width = this.progressBarTarget.clientWidth;
      let position = clientX - left;
      return Math.ceil(this.durationValue * (position / width));
    } else {
      return -1;
    }
  }

  calcCurrentIndicatorPosition(pcComplete: number): number {
    const clientWidth = this.progressBarTarget.clientWidth;

    let currentPosition, width;

    currentPosition = this.progressBarTarget.getBoundingClientRect().left - 24;

    if (clientWidth === 0) {
      width = 0;
    } else {
      // min 1rem to accomodate indicator
      const minWidth = (16 / clientWidth) * 100;
      width = pcComplete > minWidth ? pcComplete : minWidth;
    }

    if (width) {
      currentPosition += clientWidth * (width / 100);
    }

    return currentPosition;
  }

  formatTimeRemaining(value: number): string {
    if (isNaN(value) || value < 0) return '00:00:00';
    const duration = Math.floor(value);

    const hours = Math.floor(duration / 3600);
    const minutes = Math.floor((duration % 3600) / 60);
    const seconds = Math.floor(duration % 60);

    return (
      '-' +
      [hours, minutes, seconds].map((t) => t.toString().padStart(2, '0')).join(':')
    );
  }

  skipTo(position: number) {
    if (!isNaN(position) && !this.pausedValue && !this.waitingValue) {
      this.audio.currentTime = this.currentTimeValue = position;
    }
  }

  toggleActiveMode() {
    const inactive = this.pausedValue || this.waitingValue;
    if (inactive) {
      this.element.classList.add(this.inactiveClass);
      this.element.classList.remove(this.activeClass);
      this.cancelTimeUpdateTimer();
    } else {
      this.element.classList.remove(this.inactiveClass);
      this.element.classList.add(this.activeClass);
      this.startTimeUpdateTimer();
    }
  }

  initAudio() {
    console.log('initAudio');
    if (!this.audio) {
      this.audio = new Audio();
      this.audio.preload = 'metadata';

      this.audioListeners = {
        canplaythrough: this.canPlay.bind(this),
        ended: this.ended.bind(this),
        loadedmetadata: this.loadedMetaData.bind(this),
        play: this.resumed.bind(this),
        playing: this.canPlay.bind(this),
        pause: this.paused.bind(this),
        seeking: this.wait.bind(this),
        suspend: this.wait.bind(this),
        stalled: this.wait.bind(this),
        waiting: this.wait.bind(this),
        error: this.wait.bind(this),
        timeupdate: this.timeUpdate.bind(this),
      };
      Object.keys(this.audioListeners).forEach((event) =>
        this.audio.addEventListener(event, this.audioListeners[event])
      );
    }
  }

  closeAudio() {
    if (this.audio) {
      Object.keys(this.audioListeners || {}).forEach((event) =>
        this.audio.removeEventListener(event, this.audioListeners[event])
      );

      this.audio.src = '';
      this.audio.pause();
      this.audio = null;
      this.enabled = false;
    }
  }

  startTimeUpdateTimer() {
    if (!this.timeupdateTimer) {
      this.timeupdateTimer = setInterval(this.sendTimeUpdate.bind(this), 5000);
    }
  }

  cancelTimeUpdateTimer() {
    if (this.timeupdateTimer) {
      clearInterval(this.timeupdateTimer);
      this.timeupdateTimer = null;
    }
  }

  sendTimeUpdate() {
    if (this.currentTimeValue) {
      const body = new FormData();

      body.append('csrfmiddlewaretoken', this.csrfTokenValue);
      body.append('current_time', this.currentTimeValue.toString());
      body.append('playback_rate', this.playbackRateValue.toFixed(1));

      fetch(this.timeupdateUrlValue, {
        body,
        method: 'POST',
        credentials: 'same-origin',
      });
    }
  }

  set enabled(enabled: boolean) {
    if (enabled) {
      sessionStorage.setItem('player-enabled', 'true');
    } else {
      sessionStorage.removeItem('player-enabled');
    }
  }

  get enabled(): boolean {
    return !!sessionStorage.getItem('player-enabled');
  }
}
