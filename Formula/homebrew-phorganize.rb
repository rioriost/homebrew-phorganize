# Documentation: https://docs.brew.sh/Formula-Cookbook
#                https://rubydoc.brew.sh/Formula
# PLEASE REMOVE ALL GENERATED COMMENTS BEFORE SUBMITTING YOUR PULL REQUEST!
class HomebrewPhorganize < Formula
  desc "Organize the photos and the videos using embedded meta data in the files"
  homepage ""
  url "https://github.com/rioriost/homebrew-phorganize/releases/download/0.2/phorganize-v0.2.tgz"
  sha256 "ae25f151670c3e529e5da04e0758e6916fd5203b146a8be3f3937de1e17db87d"
  license ""

  # depends_on "cmake" => :build

  def install
    bin.install 'phorganize'
  end

end
