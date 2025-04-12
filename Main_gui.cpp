#include <thread>
#include <chrono>
#include "imgui.h"
#include "imgui_impl_glfw.h"
#include "imgui_impl_opengl3.h"
#include <GLFW/glfw3.h>
#include <opencv2/opencv.hpp>
#include <iostream>
#include <memory>
#include "node_image_editor.cpp"


std::shared_ptr<ImageInputNode> inputNode;
std::shared_ptr<BrightnessContrastNode> bcNode;
std::shared_ptr<OutputNode> outputNode;
GraphEngine engine;


GLuint matToTexture(const cv::Mat& mat) {
    GLuint textureID;
    glGenTextures(1, &textureID);
    glBindTexture(GL_TEXTURE_2D, textureID);

    cv::Mat rgb;
    cv::cvtColor(mat, rgb, cv::COLOR_BGR2RGB);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, rgb.cols, rgb.rows, 0, GL_RGB, GL_UNSIGNED_BYTE, rgb.data);

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    return textureID;
}

void renderGUI() {
    static char inputPath[256] = "../Input.jpg";
    static char outputPath[256] = "../Output.jpg";
    static float brightness = 0.0f;
    static float contrast = 1.0f;

    ImGui::Begin("Node Controller");
    ImGui::InputText("Input Image", inputPath, IM_ARRAYSIZE(inputPath));
    ImGui::InputText("Output Image", outputPath, IM_ARRAYSIZE(outputPath));
    ImGui::SliderFloat("Brightness", &brightness, -100.0f, 100.0f);
    ImGui::SliderFloat("Contrast", &contrast, 0.0f, 3.0f);

    if (ImGui::Button("Run Pipeline")) {
        inputNode = std::make_shared<ImageInputNode>(inputPath);
        inputNode->id = 1;

        bcNode = std::make_shared<BrightnessContrastNode>();
        bcNode->id = 2;
        bcNode->setParams({{"brightness", brightness}, {"contrast", contrast}});

        outputNode = std::make_shared<OutputNode>(outputPath);
        outputNode->id = 3;

        engine = GraphEngine();
        engine.addNode(inputNode);
        engine.addNode(bcNode);
        engine.addNode(outputNode);

        engine.connectNodes(inputNode, bcNode);
        engine.connectNodes(bcNode, outputNode);

        engine.execute();
    }

    ImGui::End();


    if (outputNode && !outputNode->result.empty()) {
        GLuint texID = matToTexture(outputNode->result);
        ImGui::Begin("Preview");
        ImGui::Image((ImTextureID)(intptr_t)texID, ImVec2(outputNode->result.cols, outputNode->result.rows));
        ImGui::End();
    }
}

int main() {

    if (!glfwInit()) return -1;

    const char* glsl_version = "#version 130";
    GLFWwindow* window = glfwCreateWindow(1280, 720, "Node-Based Image Editor", NULL, NULL);
    glfwMakeContextCurrent(window);
    glfwSwapInterval(1);


    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGuiIO& io = ImGui::GetIO();
    ImGui_ImplGlfw_InitForOpenGL(window, true);
    ImGui_ImplOpenGL3_Init(glsl_version);
    ImGui::StyleColorsDark();

    while (!glfwWindowShouldClose(window)) {
        glfwPollEvents();
        ImGui_ImplOpenGL3_NewFrame();
        ImGui_ImplGlfw_NewFrame();
        ImGui::NewFrame();

        renderGUI();

        ImGui::Render();
        int display_w, display_h;
        glfwGetFramebufferSize(window, &display_w, &display_h);
        glViewport(0, 0, display_w, display_h);
        glClearColor(0.2f, 0.2f, 0.2f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);
        ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());

        glfwSwapBuffers(window);
        std::this_thread::sleep_for(std::chrono::milliseconds(100)); 
    }


    ImGui_ImplOpenGL3_Shutdown();
    ImGui_ImplGlfw_Shutdown();
    ImGui::DestroyContext();
    glfwDestroyWindow(window);
    glfwTerminate();
    return 0;
}
