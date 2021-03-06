import '@hotwired/turbo';
import 'form-request-submit-polyfill';
import { Application } from 'stimulus';

import ConfirmController from './controllers/confirm-controller';
import DragController from './controllers/drag-controller';
import LinkController from './controllers/link-controller';
import ModalController from './controllers/modal-controller';
import NotificationController from './controllers/notification-controller';
import PlayerController from './controllers/player-controller';
import ToggleController from './controllers/toggle-controller';

// Stimulus setup
const application: Application = Application.start();

application.register('confirm', ConfirmController);
application.register('drag', DragController);
application.register('link', LinkController);
application.register('modal', ModalController);
application.register('notification', NotificationController);
application.register('player', PlayerController);
application.register('toggle', ToggleController);
