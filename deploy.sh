#!/bin/bash

# PaiNaiDee Backend - Multi-Platform Deployment Helper
# This script helps you deploy to different platforms

echo "🇹🇭 PaiNaiDee Backend Deployment Helper"
echo "======================================="
echo ""

echo "Available deployment options:"
echo "1. Railway (Recommended for production)"
echo "2. Render (Good free tier)"
echo "3. Vercel (Serverless)"
echo "4. Hugging Face Spaces (Demo/sharing)"
echo "5. GitHub Codespaces (Development)"
echo "6. Google Colab (Quick testing)"
echo "7. Local Docker"
echo ""

read -p "Choose deployment option (1-7): " choice

case $choice in
  1)
    echo "🚂 Opening Railway deployment..."
    if command -v open &> /dev/null; then
      open "https://railway.app/template/G2tGbV?referralCode=alphaDev"
    elif command -v xdg-open &> /dev/null; then
      xdg-open "https://railway.app/template/G2tGbV?referralCode=alphaDev"
    else
      echo "Visit: https://railway.app/template/G2tGbV?referralCode=alphaDev"
    fi
    ;;
  2)
    echo "🎨 Opening Render deployment..."
    if command -v open &> /dev/null; then
      open "https://render.com/deploy?repo=https://github.com/athipan1/PaiNaiDee_Backend"
    elif command -v xdg-open &> /dev/null; then
      xdg-open "https://render.com/deploy?repo=https://github.com/athipan1/PaiNaiDee_Backend"
    else
      echo "Visit: https://render.com/deploy?repo=https://github.com/athipan1/PaiNaiDee_Backend"
    fi
    ;;
  3)
    echo "⚡ Opening Vercel deployment..."
    if command -v open &> /dev/null; then
      open "https://vercel.com/new/clone?repository-url=https://github.com/athipan1/PaiNaiDee_Backend"
    elif command -v xdg-open &> /dev/null; then
      xdg-open "https://vercel.com/new/clone?repository-url=https://github.com/athipan1/PaiNaiDee_Backend"
    else
      echo "Visit: https://vercel.com/new/clone?repository-url=https://github.com/athipan1/PaiNaiDee_Backend"
    fi
    ;;
  4)
    echo "🤗 Opening Hugging Face Spaces..."
    if command -v open &> /dev/null; then
      open "https://huggingface.co/spaces/new?repo=athipan1/PaiNaiDee_Backend"
    elif command -v xdg-open &> /dev/null; then
      xdg-open "https://huggingface.co/spaces/new?repo=athipan1/PaiNaiDee_Backend"
    else
      echo "Visit: https://huggingface.co/spaces/new?repo=athipan1/PaiNaiDee_Backend"
    fi
    ;;
  5)
    echo "💻 Opening GitHub Codespaces..."
    if command -v open &> /dev/null; then
      open "https://codespaces.new/athipan1/PaiNaiDee_Backend"
    elif command -v xdg-open &> /dev/null; then
      xdg-open "https://codespaces.new/athipan1/PaiNaiDee_Backend"
    else
      echo "Visit: https://codespaces.new/athipan1/PaiNaiDee_Backend"
    fi
    ;;
  6)
    echo "📓 Opening Google Colab..."
    if command -v open &> /dev/null; then
      open "https://colab.research.google.com/github/athipan1/PaiNaiDee_Backend/blob/main/PaiNaiDee_Colab_Deploy.ipynb"
    elif command -v xdg-open &> /dev/null; then
      xdg-open "https://colab.research.google.com/github/athipan1/PaiNaiDee_Backend/blob/main/PaiNaiDee_Colab_Deploy.ipynb"
    else
      echo "Visit: https://colab.research.google.com/github/athipan1/PaiNaiDee_Backend/blob/main/PaiNaiDee_Colab_Deploy.ipynb"
    fi
    ;;
  7)
    echo "🐳 Starting local Docker deployment..."
    echo "Building Docker image..."
    if docker build -t painaidee-backend:latest .; then
      echo "✅ Docker image built successfully!"
      echo "Starting container on port 7860..."
      if docker run -p 7860:7860 -d --name painaidee-backend painaidee-backend:latest; then
        echo "✅ Container started successfully!"
        echo "🌐 Access your API at: http://localhost:7860"
        echo "🩺 Health check: http://localhost:7860/health"
        echo ""
        echo "To stop the container, run:"
        echo "docker stop painaidee-backend"
        echo "docker rm painaidee-backend"
      else
        echo "❌ Failed to start container"
      fi
    else
      echo "❌ Failed to build Docker image"
    fi
    ;;
  *)
    echo "❌ Invalid option. Please choose 1-7."
    exit 1
    ;;
esac

echo ""
echo "🎉 Thank you for using PaiNaiDee Backend!"
echo "📚 For more information, check the README.md"