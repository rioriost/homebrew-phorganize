class Phorganize < Formula
  include Language::Python::Virtualenv

  desc "Phorganize is a python script to organize photos and videos using embedded meta data in the files."
  homepage "https://github.com/rioriost/homebrew-phorganize/"
  url "https://files.pythonhosted.org/packages/cd/10/475f326fb140ecdcff79ac98037e184eab929f81b51b7a294574858401f9/phorganize-0.1.3.tar.gz"
  sha256 "fe9e2e022441d077f5af85dd7a27ca114911a12c80ac1c25af9baba9fe7d07b8"
  license "MIT"

  depends_on "python@3.11"

  resource "python-magic" do
    url "https://files.pythonhosted.org/packages/da/db/0b3e28ac047452d079d375ec6798bf76a036a08182dbb39ed38116a49130/python-magic-0.4.27.tar.gz"
    sha256 "c1ba14b08e4a5f5c31a302b7721239695b2f0f058d125bd5ce1ee36b9d9d3c3b"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/phorganize", "--help"
  end
end
