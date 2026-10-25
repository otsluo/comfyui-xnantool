import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";

// 上传 ZIP 文件到 input 目录
async function uploadZipToInput(file) {
    const form = new FormData();
    form.append("image", file, file.name);
    form.append("type", "input");
    form.append("overwrite", "true");
    const resp = await api.fetchApi("/upload/image", {
        method: "POST",
        body: form,
    });
    if (!resp.ok) {
        throw new Error(`上传失败: ${resp.status}`);
    }
    return await resp.json();
}

app.registerExtension({
    name: "XnanTool.ZipUpload",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        // 只处理 LoadZipNode
        if (nodeData.name === "LoadZipNode") {
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                if (onNodeCreated) onNodeCreated.apply(this, arguments);

                // 找到 zip_file widget
                const zipWidget = this.widgets?.find((w) => w.name === "zip_file");
                if (!zipWidget) return;
                zipWidget.label = "ZIP文件";

                // 创建文件选择器
                let input = this._xnantoolZipUploadInput;
                if (!input) {
                    input = document.createElement("input");
                    input.type = "file";
                    input.accept = ".zip,application/zip";
                    input.style.display = "none";
                    document.body.appendChild(input);
                    this._xnantoolZipUploadInput = input;
                }

                // 文件选择后的处理
                input.onchange = async () => {
                    try {
                        const f = input.files?.[0];
                        if (!f) return;
                        
                        // 上传文件
                        const res = await uploadZipToInput(f);
                        const uploadedPath = res.subfolder ? `${res.subfolder}/${res.name}` : res.name;
                        
                        // 添加到下拉列表
                        if (zipWidget.options?.values && !zipWidget.options.values.includes(uploadedPath)) {
                            zipWidget.options.values.push(uploadedPath);
                            zipWidget.options.values.sort();
                        }
                        
                        // 设置当前值
                        zipWidget.value = uploadedPath;
                        app.graph.setDirtyCanvas(true, true);
                    } catch (e) {
                        console.error("上传 ZIP 文件失败:", e);
                        alert("上传失败: " + e.message);
                    } finally {
                        input.value = "";
                    }
                };

                // 创建上传按钮
                let uploadButton = (this.widgets || []).find((w) => w?.__xnantoolZipUpload === true);
                if (!uploadButton) {
                    uploadButton = this.addWidget("button", "选择ZIP文件上传", null, () => input.click(), { serialize: false });
                    uploadButton.__xnantoolZipUpload = true;
                }
            };
        }
    },
});
