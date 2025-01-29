# Use the Rocker/verse image as the base
FROM rocker/verse:latest

# Build-time arguments for user and group IDs
ARG USER_ID=1000
ARG GROUP_ID=1000

# Install necessary dependencies and Emacs
RUN apt-get update && \
    apt-get install -y \
        emacs \
        git \
        sqlite3 \
        python3 \
        python3-pip \
        libx11-6 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set environment variable for DISPLAY
ENV DISPLAY=:0

# Install required Python packages
RUN pip3 install --break-system-packages --no-cache-dir \
    scikit-learn \
    bokeh \
    plotnine \
    jupyterlab \
    jupyter_bokeh \
    ipywidgets \
    jupyterlab_code_formatter \
    jupyterlab-git \
    nltk \
    llama_cpp_python \
    tqdm \
    openai \
    gensim \
    dspy

# Install R packages
RUN R -e "install.packages(c('gbm', 'pROC'))"

# Update the rstudio user's UID and GID
RUN groupmod -g ${GROUP_ID} rstudio && \
    usermod -u ${USER_ID} -g ${GROUP_ID} rstudio && \
    chown -R rstudio:rstudio /home/rstudio

# Set the default command to start Emacs
CMD ["emacs"]
