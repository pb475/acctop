"""
This script provides a real-time system resource monitoring tool that displays various system metrics in the terminal.
It uses the `psutil` library to gather system information and the `tabulate` library to format the output in a readable manner.

Features:
- Disk Usage: Displays total, used, and free disk space along with a colored usage bar.
- Memory Usage: Shows total, used, and available memory with a colored usage bar.
- CPU Usage: Dynamically adjusts the number of columns based on terminal width and displays per-core CPU usage with colored bars.
- User Usage: Aggregates CPU and memory usage by user and displays the process count for each user.
- Network Usage: (Optional) Displays network statistics including bytes sent/received and packets sent/received per network interface.
- Load Average: (Optional) Shows the system load average for the past 1, 5, and 15 minutes.
- System Info: (Optional) Displays system uptime and kernel version.
- Disk I/O: (Optional) Displays live disk I/O statistics including read and write bytes for each disk.

The script uses ANSI escape codes to add color to the terminal output, making it easier to read and interpret the data.

Functions:
- get_usage_color(percentage): Returns an ANSI color code based on the CPU usage percentage.
- create_cpu_usage_bar(percentage, bar_length=10): Returns a string representing an ASCII bar chart of CPU usage with color.
- create_memory_usage_bar(percentage, bar_length=30): Returns a string representing an ASCII bar chart of memory usage with color.
- create_disk_usage_bar(percentage, bar_length=30): Returns a string representing an ASCII bar chart of disk usage with color.
- display_disk_usage(): Displays disk usage statistics with a colored usage bar.
- display_memory_usage(): Displays memory usage statistics with a colored usage bar.
- get_cpu_columns(column_width): Determines the number of columns to use for CPU usage display based on terminal width.
- display_cpu_usage_in_columns(): Displays per-core CPU usage in dynamically adjusted columns with colored bars.
- display_user_usage(): Displays cumulative CPU, memory usage, and process count for each user.
- display_network_usage(): Displays network usage statistics with aligned columns and colored headers.
- display_load_average(): Displays the system load average for the past 1, 5, and 15 minutes.
- display_system_info(): Displays system uptime and kernel version.
- display_disk_io(): Displays live disk I/O statistics including read and write bytes for each disk.
- clear_console(): Clears the terminal screen.
- parse_arguments(): Parses command-line arguments for optional features and update interval.

Usage:
Run the script in a terminal to start real-time monitoring. Use command-line arguments to enable optional features and set the update interval. Press Ctrl+C to exit.
"""
import os
import psutil
import time
from collections import defaultdict
from tabulate import tabulate
import argparse

# ANSI escape codes for colors
HEADER_COLOR    = "\033[1;34m"  # Bold Blue
CPU_COLOR       = "\033[1;35m"  # Bold Magenta"
MEMORY_COLOR    = "\033[1;35m"  # Bold Magenta"
DISK_COLOR      = "\033[1;35m"  # Bold Magenta"
NETWORK_COLOR   = "\033[1;35m"  # Bold Magenta
USER_COLOR      = "\033[1;35m"  # Bold Magenta"
LOAD_COLOR      = "\033[1;35m"  # Bold Magenta"
INFO_COLOR      = "\033[1;35m"  # Bold Magenta"
RESET_COLOR     = "\033[0m"     # Reset to default
lencolors = len(HEADER_COLOR) + len(RESET_COLOR)

# Additional ANSI escape codes for CPU and memory usage bars
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"

def get_usage_color(percentage):
    """Returns an ANSI color code based on the CPU usage percentage."""
    if percentage < 50:
        return GREEN
    elif percentage < 80:
        return YELLOW
    else:
        return RED

def create_cpu_usage_bar(percentage, bar_length=10):
    """Returns a string representing an ASCII bar chart of CPU usage with color."""
    color = get_usage_color(percentage)
    num_bars = int((percentage / 100) * bar_length)
    return f"{color}[{'#' * num_bars}{' ' * (bar_length - num_bars)}] {percentage:6.2f}%{RESET_COLOR}"

def create_memory_usage_bar(percentage, bar_length=30):
    """Returns a string representing an ASCII bar chart of memory usage with color."""
    color = get_usage_color(percentage)
    num_bars = int((percentage / 100) * bar_length)
    return f"{color}[{'#' * num_bars}{' ' * (bar_length - num_bars)}] {percentage:6.2f}%{RESET_COLOR}"

def create_disk_usage_bar(percentage, bar_length=30):
    """
    Generate an ASCII bar chart representing disk usage with color.
    Args:
        percentage (float): The disk usage percentage.
        bar_length (int, optional): The length of the bar. Defaults to 30.
    Returns:
        str: A string representing the colored ASCII bar chart of disk usage.
    """

    color = get_usage_color(percentage)
    num_bars = int((percentage / 100) * bar_length)
    return f"{color}[{'#' * num_bars}{' ' * (bar_length - num_bars)}] {percentage:6.2f}%{RESET_COLOR}"

def display_disk_usage():
    """
    Displays the disk usage statistics for all mounted disks including total, used,
    and free space in gigabytes or terabytes, along with a visual usage bar.
    """

    def format_size(size):
        """Helper function to format the size in GB or TB."""
        if size >= 1024 ** 4:  # Size in TB
            return f"{size / (1024 ** 4):.2f} TB"
        else:  # Size in GB
            return f"{size / (1024 ** 3):.2f} GB"

    disk_usage_header = f"{DISK_COLOR}=== Disk Usage ==={RESET_COLOR}"
    partitions = psutil.disk_partitions()
    table_data = []
    for partition in partitions:
        try:
            disk_usage = psutil.disk_usage(partition.mountpoint)
            usage_percentage = disk_usage.percent
            table_data.append([
                partition.mountpoint,
                format_size(disk_usage.total),
                format_size(disk_usage.used),
                format_size(disk_usage.free),
                create_disk_usage_bar(usage_percentage)
            ])
        except PermissionError:
            # This can happen on some systems where certain partitions are not accessible
            table_data.append([
                partition.mountpoint,
                "Permission Denied",
                "Permission Denied",
                "Permission Denied",
                "Permission Denied"
            ])

    headers = ["Mountpoint", "Total", "Used", "Free", "Usage"]
    colalign = ("left", "right", "right", "right", "left")
    table = tabulate(table_data, headers=headers, tablefmt="pretty", colalign=colalign)
    return f"{disk_usage_header}\n" + table + "\n"

def display_memory_usage():
    """
    Display the current memory and swap usage statistics.
    This function retrieves memory and swap usage information using the `psutil` library,
    formats the data, and prints it in a human-readable format. The output includes the
    total, used, and available memory in gigabytes (GB), as well as a visual representation
    of memory usage as a bar.
    The function prints the following information:
    - Total memory in GB
    - Used memory in GB
    - Available memory in GB
    - Memory usage bar
    Note:
        This function assumes that the `psutil` library is installed and available.
        It also uses some global variables for color formatting (`MEMORY_COLOR`, `RESET_COLOR`).
    Example:
        >>> display_memory_usage()
        === Memory Usage ===
        Total: 16.00 GB | Used: 8.00 GB | Available: 7.50 GB | [##########          ]
    """

    memory_info = psutil.virtual_memory()
    swap_info = psutil.swap_memory()
    # TODO: we could consider displaying the swap usage as well

    # get Memory Usage in a nice format
    memory_usage_header = f"{MEMORY_COLOR}=== Memory Usage ==={RESET_COLOR}"
    memory_usage_info = (
        f"Total: {f'{memory_info.total / (1024 ** 3):.2f} GB'} | "
        f"Used: {f'{memory_info.used / (1024 ** 3):.2f} GB'} | "
        f"Available: {f'{memory_info.available / (1024 ** 3):.2f} GB'} | "
        f"{f'{create_memory_usage_bar(memory_info.percent)}'}"
    )
    return f"{memory_usage_header}\n{memory_usage_info}\n"

def get_cpu_columns(column_width):
    """
    Determine the number of CPU columns to display based on the terminal width.
    This function calculates the number of columns to use for displaying CPU information
    based on the width of the terminal and a given column width. It returns a value between
    1 and 5, where 1 indicates a narrow terminal and 5 indicates an extra extra wide terminal.
    Args:
        column_width (int): The width of a single column.
    Returns:
        int: The number of columns to use for displaying CPU information. Possible values are:
             - 1: Narrow terminal
             - 2: Medium terminal
             - 3: Wide terminal
             - 4: Extra wide terminal
             - 5: Extra extra wide terminal
             - 2: Default if terminal size cannot be determined
    """

    try:
        terminal_width = os.get_terminal_size().columns
        return terminal_width // column_width
    except OSError:
        return 1  # Default to 2 columns if terminal size cannot be determined

def display_cpu_usage_in_columns():
    """
    Display CPU usage for each core in a formatted column layout.
    This function retrieves the CPU usage percentages for each core,
    formats them into columns based on the terminal width, and prints
    the usage bars along with the core labels. It also prints the average
    CPU usage at the end.
    """

    cpu_usage_header = f"{CPU_COLOR}=== CPU Usage ==={RESET_COLOR}"

    cpu_percentages = psutil.cpu_percent(percpu=True)

    # Determine the width needed for the core labels, bars, and percentages
    num_cores = len(cpu_percentages)

    core_label_width = len("Core ")  # Default width for the core label
    core_number_width = len(str(num_cores))  # Width of the core number
    core_joined_label_width = core_label_width+core_number_width  # Width of the core label with number
    max_bar_length = max(len(create_cpu_usage_bar(p).rstrip()) for p in cpu_percentages)-lencolors # Max bar length for the bars, the minus lencolors is to remove the html color codes

    # Total column width (bar + percentage + spacing)
    column_width = core_joined_label_width + max_bar_length + len(": ") + 5 # Extra space for padding to match with the bar padding in loop below

    # Determine the number of columns based on terminal width and the column display width
    columns = get_cpu_columns(column_width) # just do one less column

    # Prepare rows for display based on the number of columns
    row_format = "".join([f"{{:<{column_width}}}" for _ in range(columns)])

    # Prepare the data to be displayed in rows
    row_data = []
    cpu_usage_rows = ""
    for i, percentage in enumerate(cpu_percentages):
        bar = create_cpu_usage_bar(percentage)
        entry = f"Core {i:>{core_number_width}}: {bar}  "
        row_data.append(entry)

        # When we have enough data for a full row or it's the last core, append the row
        if (i + 1) % columns == 0 or i == len(cpu_percentages) - 1:
            # Pad the row if necessary (if not enough columns are filled)
            while len(row_data) < columns:
                row_data.append(" " * column_width)  # Add empty string to fill the columns
            cpu_usage_rows += row_format.format(*row_data) + "\n"
            row_data = []  # Reset for the next row
    average_cpu_usage = sum(cpu_percentages) / len(cpu_percentages)
    average_cpu_usage_string = f"Average CPU Usage: {create_cpu_usage_bar(average_cpu_usage)}"
    return f'{cpu_usage_header}\n{cpu_usage_rows}{average_cpu_usage_string}\n'

def display_user_usage():
    """
    Display cumulative CPU, memory usage, and process count for each user.
    This function iterates over all running processes, accumulates CPU and memory usage,
    and counts the number of processes for each user. It then filters users based on
    specified CPU and memory usage thresholds and displays the results in a formatted table.
    """

    cumulative_user_usage_header = f"{USER_COLOR}=== Cumulative User CPU, Memory Usage, and Process Count ==={RESET_COLOR}"

    # Define thresholds
    cpu_threshold = 0.01  # CPU usage threshold in percent
    memory_threshold = 0.01  # Memory usage threshold in percent

    # Dictionary to store cumulative CPU, memory usage, and process count for each user
    user_usage = defaultdict(lambda: {'cpu': 0.0, 'memory': 0.0, 'processes': 0})

    # Get the number of CPUs (cores)
    num_cpus = psutil.cpu_count()

    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
        try:
            # Get process information
            proc_info = proc.info
            username = proc_info['username']
            if username:  # Ensure the process has a valid username
                # Accumulate the CPU and memory usage for each user
                user_data = user_usage[username]
                user_data['cpu'] += proc_info['cpu_percent']
                user_data['memory'] += proc_info['memory_percent']
                # Increment the process count for the user
                user_data['processes'] += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Filter users based on the thresholds
    filtered_user_data = [
        {
            'Username': user,
            'CPU Usage (%)': f"{get_usage_color((usage['cpu'] / num_cpus))}{(usage['cpu'] / num_cpus):.2f}{RESET_COLOR}",
            'Memory Usage (%)': f"{get_usage_color(usage['memory'])}{usage['memory']:.2f}{RESET_COLOR}",
            'Process Count': usage['processes']
        }
        for user, usage in user_usage.items()
        if (usage['cpu'] / num_cpus) > cpu_threshold or usage['memory'] > memory_threshold
    ]

    # Display the filtered data in a table
    if filtered_user_data:
        colalign = ("left", "right", "right", "right")
        return f'{cumulative_user_usage_header}\n' + tabulate(filtered_user_data, headers='keys', tablefmt="pretty", colalign=colalign) + "\n"
    else:
        return "No users exceed the specified thresholds.\n"

def display_network_usage():
    """
    Display network usage statistics including bytes sent, bytes received,
    packets sent, and packets received for each network interface.
    """

    network_usage_header = f"{NETWORK_COLOR}=== Network Usage ==={RESET_COLOR}"

    net_io = psutil.net_io_counters(pernic=True) # Get network I/O statistics per network interface

    # Column titles
    coltitle_interface = "Interface"
    coltitle_megabytes_sent = "Bytes Sent (MB)"
    coltitle_megabytes_recv = "Bytes Received (MB)"
    coltitle_packets_sent = "Packets Sent"
    coltitle_packets_recv = "Packets Received"

    table_data = []
    for interface, stats in net_io.items():
        row = [
            interface,
            f"{stats.bytes_sent / (1024 ** 2):.2f}",
            f"{stats.bytes_recv / (1024 ** 2):.2f}",
            stats.packets_sent,
            stats.packets_recv
        ]
        table_data.append(row)

    headers = [coltitle_interface, coltitle_megabytes_sent, coltitle_megabytes_recv, coltitle_packets_sent, coltitle_packets_recv]
    colalign = ("left", "right", "right", "right", "right")
    table = tabulate(table_data, headers=headers, tablefmt="pretty", colalign=colalign)
    return f"{network_usage_header}\n{table}\n"

def display_load_average():
    """
    Display the system load averages for the past 1, 5, and 15 minutes.
    """

    load_average_header = f"{LOAD_COLOR}=== Load Average ==={RESET_COLOR}"

    load_avg = os.getloadavg()  # Returns a tuple of (1min, 5min, 15min load averages)
    load_averages = (f"1 min: {load_avg[0]:.2f} | "
                    f"5 min: {load_avg[1]:.2f} | "
                    f"15 min: {load_avg[2]:.2f}")
    return f"{load_average_header}\n{load_averages}\n"

def display_system_info():
    """
    Displays system information including uptime and kernel version.
    """

    system_info_header = f"{INFO_COLOR}=== System Info ==={RESET_COLOR}"
    uptime_seconds = time.time() - psutil.boot_time()
    uptime = time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))
    kernel_version = os.uname().release
    return f"{system_info_header}\nUptime: {uptime}\nKernel Version: {kernel_version}\n"

def display_disk_io():
    """
    Display live disk I/O statistics including read and write bytes for each disk.
    """

    # Define header
    disk_io_header = (f"{DISK_COLOR}=== Disk I/O ==={RESET_COLOR}")

    # Get disk I/O statistics
    disk_io = psutil.disk_io_counters(perdisk=True)

    # Column titles
    coltitle_disk = "Disk"
    coltitle_readwrite_speed = "Read/Write (MB/s)"

    # Determine the width of each column
    disk_width = max(max(len(disk) for disk in disk_io.keys()), len(coltitle_disk))
    max_readwrite_speed_len = len(coltitle_readwrite_speed)+8

    # Header row with colored titles
    header = (f"{HEADER_COLOR}{coltitle_disk.ljust(disk_width)} | "
              f"{coltitle_readwrite_speed.ljust(max_readwrite_speed_len)}{RESET_COLOR}")

    # Determine the width of the combined tables
    combined_width = disk_width+max_readwrite_speed_len  # Adding some space between the tables

    # Store previous I/O stats to calculate speed
    prev_disk_io = psutil.disk_io_counters(perdisk=True)
    poll_interval = 0.01  # Polling interval in seconds
    time.sleep(poll_interval)  # Sleep for 1 second to calculate speed
    curr_disk_io = psutil.disk_io_counters(perdisk=True)

    # Get the console width
    terminal_width = os.get_terminal_size().columns

    # Check if the terminal width is sufficient to display tables side by side
    N = min(terminal_width // combined_width, 10)
    N = max(N, 1)  # Ensure at least 1 table is displayed

    # Data rows
    tables = [[] for _ in range(N)]  # Create N empty tables
    for i, (disk, stats) in enumerate(curr_disk_io.items()):
        prev_stats = prev_disk_io[disk]
        read_speed = (1.0 / poll_interval) * (stats.read_bytes - prev_stats.read_bytes) / (1024 ** 2)  # MB/s
        write_speed = (1.0 / poll_interval) * (stats.write_bytes - prev_stats.write_bytes) / (1024 ** 2)  # MB/s
        row = f"{disk.ljust(disk_width)} | {read_speed:.2f}/{write_speed:.2f}".ljust(max_readwrite_speed_len)
        tables[i % N].append(row)

    # Function to return tables side by side
    def tables_side_by_side(tables):
        max_len = max(len(table) for table in tables)
        disk_io_rows = []
        for i in range(max_len):
            row_parts = []
            for table in tables:
                if i < len(table):
                    row_parts.append(table[i])
                else:
                    row_parts.append(" " * len(header))
            row_parts.append(" " * len(header))
        disk_io_rows.append(" ".join(row_parts))
        return "\n".join(disk_io_rows)

    return f'{disk_io_header}\n' + header +'\n'+ tables_side_by_side(tables)

def clear_console():
    """
    Clears the console screen. Works on both Windows and Unix-like systems.
    """

    os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == "__main__":

    def parse_arguments():
        """
        Parses command-line arguments for the Real-Time System Resource Monitoring Tool.
        Returns:
            argparse.Namespace: Parsed command-line arguments.
        """

        # Parse command-line arguments
        parser = argparse.ArgumentParser(description="Real-Time System Resource Monitoring Tool")
        parser.add_argument('--interval', type=float, default=5, help='Update interval in seconds (default: 5)')
        parser.add_argument('--show-network', action='store_true', help='Display network usage')
        parser.add_argument('--show-load', action='store_true', help='Display load average')
        parser.add_argument('--show-system', action='store_true', help='Display system info')
        parser.add_argument('--show-disk-io', action='store_true', help='Display disk I/O statistics')
        parser.add_argument('--show-all', action='store_true', help='Display all optional features')
        parser.add_argument('--show-most', action='store_true', help='Display all optional features')
        return parser.parse_args()

    args = parse_arguments()
    try:
        clear_console()  # Clear the screen
        while True:

            # Create the output to be displayed
            output = []
            output.append(f"{HEADER_COLOR}=== Real-Time System Resource Usage for {os.uname().nodename.capitalize()} ==={RESET_COLOR}")
            output.append(display_disk_usage())  # Disk usage with a bar
            output.append(display_memory_usage())  # Memory usage with a bar
            output.append(display_cpu_usage_in_columns())  # Dynamically set number of columns based on terminal width
            output.append(display_user_usage())  # Cumulative user usage with CPU normalized by number of cores
            if args.show_network or args.show_all:
                output.append(display_network_usage())  # Network usage with aligned columns and colored headers
            if args.show_load or args.show_all:
                output.append(display_load_average())  # Load average
            if args.show_system or args.show_all:
                output.append(display_system_info())  # System uptime and kernel version
            if args.show_disk_io or args.show_all or args.show_most:
                output.append(display_disk_io())
            output.append(f"{HEADER_COLOR}========================================{RESET_COLOR}")
            output.append('Press ctrl+c to exit...')

            # Print the output all at once
            print("\n".join(output))

            # Wait for the specified interval and clear the console
            time.sleep(args.interval)  # Update based on the interval argument
            clear_console()  # Clear the screen

    except KeyboardInterrupt:
        print("\nExiting real-time monitoring.")
