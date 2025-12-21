# Logging Configuration

Both `SwitchBoard` and `Reactor` now support file-based logging in addition to console output. This allows for persistent logs that can be easily collected and analyzed, especially when integrating with tools like Flux.

## Configuration

Logging behavior can be controlled using the following environment variables:

*   **`LOG_LEVEL`**: Sets the minimum level of messages to log (e.g., `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). Defaults to `INFO`.
*   **`LOG_FILE`**: Specifies the path to the log file. If this variable is not set, logs will be written to `switchboard.log` for `SwitchBoard` and `reactor.log` for `Reactor` in their respective directories.

## Example Usage

To enable file logging and set the log level, you can create or modify your `.env` files for `SwitchBoard` (in `WindFlag/SwitchBoard/.env`) and `Reactor` (in `WindFlag/Reactor/reactor_agent/.env`) or set these variables directly in your environment.

### Example for `SwitchBoard`'s `.env` (e.g., `WindFlag/SwitchBoard/.env`)

```
LOG_LEVEL=DEBUG
LOG_FILE=/var/log/switchboard/switchboard.log
```

### Example for `Reactor`'s `.env` (e.g., `WindFlag/Reactor/reactor_agent/.env`)

```
LOG_LEVEL=DEBUG
LOG_FILE=/var/log/reactor/reactor.log
```

**Note**: Ensure that the directories specified in `LOG_FILE` (e.g., `/var/log/switchboard/` and `/var/log/reactor/`) exist and that the application has write permissions to them.
