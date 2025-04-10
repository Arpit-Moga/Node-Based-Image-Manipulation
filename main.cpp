// Node-Based Image Manipulation Interface - Core Implementation

#include <iostream>
#include <opencv2/opencv.hpp>
#include <unordered_map>
#include <vector>
#include <memory>
#include <set>
#include <string>

// Abstract base class for all nodes
class Node {
public:
    int id;
    std::string name;
    std::vector<std::shared_ptr<Node>> inputs;
    cv::Mat result;

    virtual void process() = 0;
    virtual void setParams(const std::unordered_map<std::string, double>& params) {}
    virtual ~Node() = default;
};

// Image Input Node
class ImageInputNode : public Node {
    std::string path;
public:
    ImageInputNode(const std::string& imgPath) {
        path = imgPath;
        name = "ImageInput";
    }

    void process() override {
        result = cv::imread(path);
        if (result.empty()) {
            std::cerr << "Failed to load image: " << path << std::endl;
        }
    }
};

// Brightness/Contrast Node
class BrightnessContrastNode : public Node {
    double brightness = 0.0; // -100 to +100
    double contrast = 1.0;   // 0 to 3
public:
    BrightnessContrastNode() {
        name = "BrightnessContrast";
    }

    void setParams(const std::unordered_map<std::string, double>& params) override {
        if (params.count("brightness")) brightness = params.at("brightness");
        if (params.count("contrast")) contrast = params.at("contrast");
    }

    void process() override {
        if (inputs.empty() || inputs[0]->result.empty()) return;
        cv::Mat input = inputs[0]->result;
        input.convertTo(result, -1, contrast, brightness);
    }
};

// Output Node
class OutputNode : public Node {
    std::string outPath;
public:
    OutputNode(const std::string& path) {
        outPath = path;
        name = "Output";
    }

    void process() override {
        if (inputs.empty() || inputs[0]->result.empty()) return;
        result = inputs[0]->result;
        cv::imwrite(outPath, result);
    }
};

// Graph Engine
class GraphEngine {
    std::unordered_map<int, std::shared_ptr<Node>> nodes;
    std::set<int> visited;
    std::set<int> visiting;

    bool dfs(std::shared_ptr<Node> node) {
        if (visited.count(node->id)) return true;
        if (visiting.count(node->id)) return false;
        visiting.insert(node->id);
        for (auto& input : node->inputs) {
            if (!dfs(input)) return false;
        }
        node->process();
        visiting.erase(node->id);
        visited.insert(node->id);
        return true;
    }

public:
    void addNode(std::shared_ptr<Node> node) {
        nodes[node->id] = node;
    }

    void connectNodes(std::shared_ptr<Node> from, std::shared_ptr<Node> to) {
        to->inputs.push_back(from);
    }

    bool execute() {
        visited.clear();
        visiting.clear();
        for (auto& pair : nodes) {
            if (!dfs(pair.second)) {
                std::cerr << "Cycle detected in graph!" << std::endl;
                return false;
            }
        }
        return true;
    }
};

int main() {
    GraphEngine engine;

    auto input = std::make_shared<ImageInputNode>("input.jpg");
    input->id = 1;

    auto bc = std::make_shared<BrightnessContrastNode>();
    bc->id = 2;
    bc->setParams({{"brightness", 50}, {"contrast", 1.5}});

    auto output = std::make_shared<OutputNode>("output.jpg");
    output->id = 3;

    engine.addNode(input);
    engine.addNode(bc);
    engine.addNode(output);

    engine.connectNodes(input, bc);
    engine.connectNodes(bc, output);

    engine.execute();

    std::cout << "Processing complete." << std::endl;
    return 0;
}
