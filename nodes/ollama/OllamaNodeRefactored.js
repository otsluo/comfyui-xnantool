import { app } from "/scripts/app.js";

app.registerExtension({
  name: "Comfy.OllamaNode",
  async beforeRegisterNodeDef(nodeType, nodeData, app) {
    if (["OllamaGenerateRefactored", "OllamaChatRefactored", "OllamaConnectivityRefactored", "OllamaOptionsRefactored"].includes(nodeData.name)) {
      const originalNodeCreated = nodeType.prototype.onNodeCreated;
      nodeType.prototype.onNodeCreated = async function () {
        if (originalNodeCreated) {
          originalNodeCreated.apply(this, arguments);
        }

        const urlWidget = this.widgets.find((w) => w.name === "url");
        const modelWidget = this.widgets.find((w) => w.name === "model");
        let refreshButtonWidget = {};
        if (["OllamaConnectivityRefactored"].includes(nodeData.name)) {
          refreshButtonWidget = this.addWidget("button", "🔄 Reconnect");
        }

        const fetchModels = async (url) => {
          const response = await fetch("/ollama/get_models", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ url }),
          });

          if (response.ok) {
            return await response.json();
          } else {
            throw new Error(response);
          }
        };

        const updateModels = async () => {
          refreshButtonWidget.name = "⏳ Fetching...";
          const url = urlWidget.value;

          let models = [];
          try {
            models = await fetchModels(url);
          } catch (error) {
            console.error("Error fetching models:", error);
            app.extensionManager.toast.add({
              severity: "error",
              summary: "Ollama connection error",
              detail: "Make sure Ollama server is running",
              life: 5000,
            });
            refreshButtonWidget.name = "🔄 Reconnect";
            this.setDirtyCanvas(true);
            return;
          }

          const prevValue = modelWidget.value;

          // Update modelWidget options and value
          modelWidget.options.values = models;

          if (models.includes(prevValue)) {
            modelWidget.value = prevValue; // stay on current.
          } else if (models.length > 0) {
            modelWidget.value = models[0]; // set first as default.
          }

          refreshButtonWidget.name = "🔄 Reconnect";
          this.setDirtyCanvas(true);
        };

        urlWidget.callback = updateModels;
        refreshButtonWidget.callback = updateModels;

        // Initial update
        await updateModels();
      };
    }
  },
});
