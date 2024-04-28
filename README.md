# PMA (Proactive Microservices AutoScaler)

## Overview
PMA is a MAPE-K-based self-adaptive system that proactively adapts microservices at runtime. PMA is a generic, holistic, adaptive, proactive system that aims to manage microservices through horizontal auto-scaling. It offers three forecasting strategies: univariate, multivariate, and MPS. These strategies estimate the usage of performance metrics for a particular microservice at runtime. Based on this estimation, the system decides whether an adaptation is needed. If necessary, the adaptation consists of executing scaling-in/scaling-out operations. 

## Key Features
- **Self-Adaptive Scaling**: PMA continuously monitors your microservices application and dynamically adjusts the number of instances based on workload demand, ensuring optimal performance and resource utilization.
- **Proactive Optimization**: By analyzing various metrics such as CPU usage, memory consumption, and incoming traffic, PMA anticipates scalability needs and proactively scales resources before performance degradation occurs.
- **Customizable Policies**: Tailor scaling policies to match your application's unique requirements. Define thresholds and triggers to initiate scaling actions, providing fine-grained control over resource allocation.
- **Easy Integration**: With a simple setup process and intuitive configuration options, PMA seamlessly integrates into your existing microservices environment, requiring minimal effort for implementation and maintenance.


## Installation
To install PMA, follow these steps:

1. Clone the repository to your local machine:
    ```
    git clone https://github.com/yourusername/PMA.git
    ```

2. Navigate to the project directory:
    ```
    cd PMA
    ```

3. Install the required dependencies using pip:
    ```
    pip3 install -r requirements.txt
    ```

## Usage
After installing PMA, you can use it to auto-scale your microservices applications. Follow these steps to set up auto-scaling:

1. Configure PMA to monitor your microservices application by editing the configuration file (`mape-k.py`) with relevant metrics thresholds and scaling policies. PMA can also be customized to adapt to your specific microservices application and scaling requirements. You can modify the configuration file (`mape-k.yaml`) to set custom thresholds and scaling policies tailored to your application's needs.

2. Run PMA using the following command:
    ```
    python3 mape-k.py
    ```

3. PMA will continuously monitor the metrics of your microservices application and automatically adjust the number of instances based on the defined scaling policies.

## Contributing
Contributions to PMA are welcome! If you find any issues or have suggestions for improvements, feel free to open an issue or submit a pull request on GitHub.

## License
This project is licensed under the Creative Commons License - see the [LICENSE](https://creativecommons.org/licenses/by-sa/4.0/) file for details.

## Contact
For any questions or inquiries about PMA, feel free to contact us at [wellisonraulm@gmail.com](mailto:wellisonraulm@gmail.com).

Optimize your microservices application with PMA's self-adaptive proactive auto-scaling! 🚀
