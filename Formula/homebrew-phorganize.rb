# Documentation: https://docs.brew.sh/Formula-Cookbook
#                https://rubydoc.brew.sh/Formula
# PLEASE REMOVE ALL GENERATED COMMENTS BEFORE SUBMITTING YOUR PULL REQUEST!
class HomebrewPhorganize < Formula
  desc "Organize the photos and the videos using embedded meta data in the files"
  homepage ""
  url "https://github.com/rioriost/homebrew-phorganize/releases/download/0.1/phorganize-v0.1.tgz"
  sha256 "565482fc27a11d0f82c4ad2d04026242d0e371886f12d6f60a4384e4bf52f718"
  license ""

  # depends_on "cmake" => :build

  def install
    bin.install 'phorganize'
  end

end
